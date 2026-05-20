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
        self.rpc_url = "https://rpc.tempo.xyz"
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
        url = f"https://coins.llama.fi/block/tempo/{timestamp}"
        response = await retry_get_json(url)
        block_number = response["height"]
        block_ts = response["timestamp"]
        tries = 0

        while block_ts > timestamp:
            if tries > 5:
                log.error(
                    "Couldn't find closest block before %s. Using %s as closest alternative",
                    timestamp,
                    block_number,
                )
                break
            block_number -= 1
            block = await self._get_block_by_number(hex(block_number))
            block_ts = int(block["timestamp"], 16)
            tries += 1

        return block_number

    async def _get_block_by_number(self, block_number):
        payload = {
            "jsonrpc": "2.0",
            "method": "eth_getBlockByNumber",
            "params": [block_number, False],
            "id": 1,
        }
        response = await retry_post_json(self.rpc_url, json=payload)
        return response["result"]
