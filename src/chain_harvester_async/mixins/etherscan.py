import json
import logging
import urllib.parse

from chain_harvester_async.mixins.base import BaseExplorerMixin
from environs import env

from chain_harvester.exceptions import ChainException
from chain_harvester_async.utils.http import retry_get_json

log = logging.getLogger(__name__)


class EtherscanMixin(BaseExplorerMixin):
    def __init__(
        self,
        etherscan_api_key=None,
        *args,
        **kwargs,
    ):
        self.etherscan_api_key = etherscan_api_key or env("ETHERSCAN_API_KEY", None)
        self.etherscan_url = "https://api.etherscan.io/v2"
        super().__init__(*args, **kwargs)

    async def get_abi_from_source(self, contract_address):
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

    async def get_block_for_timestamp_fallback(self, timestamp):
        query_params = {
            "chainid": self.chain_id,
            "module": "block",
            "action": "getblocknobytime",
            "timestamp": timestamp,
            "closest": "before",
            "apikey": self.etherscan_api_key,
        }
        url = f"{self.etherscan_url}/api?{urllib.parse.urlencode(query_params)}"
        data = await retry_get_json(url)
        result = int(data["result"])
        return result
