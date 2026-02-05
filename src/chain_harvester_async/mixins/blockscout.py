import logging
import urllib.parse

from chain_harvester_async.mixins.base import BaseExplorerMixin
from chain_harvester_async.utils.http import retry_get_json

log = logging.getLogger(__name__)


class BlockscoutMixin(BaseExplorerMixin):
    def __init__(
        self,
        blockscout_url,
        *args,
        **kwargs,
    ):
        self.blockscout_url = blockscout_url
        super().__init__(*args, **kwargs)

    async def get_abi_from_source(self, contract_address):
        url = f"{self.blockscout_url}/api/v2/smart-contracts/{contract_address.lower()}"
        try:
            data = await retry_get_json(url, timeout=5)
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
            "module": "block",
            "action": "getblocknobytime",
            "timestamp": timestamp,
            "closest": "before",
        }
        url = f"{self.blockscout_url}/api?{urllib.parse.urlencode(query_params)}"
        data = await retry_get_json(url)
        result = int(data["result"]["blockNumber"])
        return result
