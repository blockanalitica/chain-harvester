import logging

from chain_harvester.exceptions import ChainException
from chain_harvester_async.mixins.base import BaseExplorerMixin
from chain_harvester_async.utils.http import retry_get_json, retry_post_json

log = logging.getLogger(__name__)


class TempoMixin(BaseExplorerMixin):
    def __init__(
        self,
        *args,
        **kwargs,
    ):
        self.api = "https://contracts.tempo.xyz/v2"
        self.rpc_url = f"https://tempo-mainnet.g.alchemy.com/v2/{self.alchemy_api_key}"
        super().__init__(*args, **kwargs)

    async def get_abi_from_source(self, contract_address):
        url = f"{self.api}/contract/{self.chain_id}/{contract_address}?fields=abi"

        try:
            data = await retry_get_json(url, timeout=5)
        except TimeoutError:
            log.exception(
                "Timeout when getting abi from %s",
                self.api,
                extra={"contract_address": contract_address},
            )
            raise

        if data.get("match") != "exact_match":
            raise ChainException(f"Request to {self.api} failed: {data['message']}")

        abi = data["abi"]
        return abi

    async def get_closest_block_before_timestamp(self, timestamp):
        latest_block = await self._get_block_by_number("latest")
        low = 0
        high = int(latest_block["number"], 16)

        while low < high:
            mid_block_number = (low + high + 1) // 2
            mid_block = await self._get_block_by_number(hex(mid_block_number))
            mid_block_timestamp = int(mid_block["timestamp"], 16)

            if mid_block_timestamp <= timestamp:
                low = mid_block_number
            else:
                high = mid_block_number - 1

        return low

    async def _get_block_by_number(self, block_number):
        payload = {
            "jsonrpc": "2.0",
            "method": "eth_getBlockByNumber",
            "params": [block_number, False],
            "id": 1,
        }
        response = await retry_post_json(self.rpc_url, json=payload)
        return response["result"]
