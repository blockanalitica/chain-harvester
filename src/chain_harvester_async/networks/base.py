import json
import logging
import urllib.parse

from environs import env

from chain_harvester.exceptions import ChainException
from chain_harvester_async.chain import Chain
from chain_harvester_async.mixins import BlockscoutMixin
from chain_harvester_async.utils.http import retry_get_json

log = logging.getLogger(__name__)


class BaseMainnetChain(BlockscoutMixin, Chain):
    latest_block_offset = 30

    def __init__(self, *args, etherscan_api_key=None, **kwargs):
        self.etherscan_api_key = etherscan_api_key or env("ETHERSCAN_API_KEY", None)
        self.etherscan_url = "https://api.etherscan.io/v2"
        super().__init__(*args, chain="base", network="mainnet", **kwargs)

    async def get_abi_from_source(self, contract_address):
        """
        We still want to use etherscan to fetch abi's, because blockscout is unreliable for
        fetching ABIs. Basically the only reason we use blockscout is in order to be able to
        call `get_closest_block_before_timestamp` which basescan doesnt support.
        """
        query_params = {
            "chainid": self.chain_id,
            "module": "contract",
            "action": "getabi",
            "address": contract_address,
            "apikey": self.etherscan_api_key,
        }
        url = f"{self.etherscan_url}/api?{urllib.parse.urlencode(query_params)}"

        try:
            data = await retry_get_json(url, timeout=5)
        except TimeoutError:
            log.exception(
                "Timeout when getting abi from %s",
                self.etherscan_url,
                extra={"contract_address": contract_address},
            )
            raise

        if data["status"] != "1":
            raise ChainException(f"Request to {self.etherscan_url} failed: {data['result']}")

        abi = json.loads(data["result"])
        return abi
