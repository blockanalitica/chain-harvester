import logging
import urllib.parse

from environs import env

from chain_harvester_async.mixins.base import BaseExplorerMixin
from chain_harvester_async.utils.http import retry_get_json

log = logging.getLogger(__name__)


class BlockscoutMixin(BaseExplorerMixin):
    def __init__(self, blockscout_api_key=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.blockscout_api_key = blockscout_api_key or env("BLOCKSCOUT_API_KEY", None)
        self.blockscout_url = f"https://api.blockscout.com/{self.chain_id}/api"
        self.headers = {"Authorization": f"Bearer {self.blockscout_api_key}"}

    async def get_abi_from_source(self, contract_address):
        url = f"{self.blockscout_url}/v2/smart-contracts/{contract_address.lower()}"
        try:
            data = await retry_get_json(url, headers=self.headers, timeout=5)
        except TimeoutError:
            log.exception(
                "Timeout when get abi from %s",
                self.blockscout_url,
                extra={"contract_address": contract_address},
            )
            raise

        return data["abi"]

    async def get_block_for_timestamp_fallback(self, timestamp):
        query_params = {
            "chainid": self.chain_id,
            "module": "block",
            "action": "getblocknobytime",
            "timestamp": timestamp,
            "closest": "before",
        }
        url = f"{self.blockscout_url}/?{urllib.parse.urlencode(query_params)}"
        data = await retry_get_json(url, headers=self.headers, timeout=5)
        result = int(data["result"]["blockNumber"])
        return result
