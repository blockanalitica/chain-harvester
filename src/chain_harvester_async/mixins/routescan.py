import json
import logging
import urllib.parse

from chain_harvester.exceptions import ChainException
from chain_harvester_async.mixins.base import BaseExplorerMixin
from chain_harvester_async.utils.http import retry_get_json

log = logging.getLogger(__name__)


class RoutescanMixin(BaseExplorerMixin):
    def _get_url(self):
        return f"https://api.routescan.io/v2/network/mainnet/evm/{self.chain_id}/etherscan/api"

    async def get_abi_from_source(self, contract_address):
        query_params = {
            "module": "contract",
            "action": "getabi",
            "address": contract_address,
        }
        url = f"{self._get_url()}?{urllib.parse.urlencode(query_params)}"

        try:
            data = await retry_get_json(url, timeout=5)
        except TimeoutError:
            log.exception(
                "Timeout when getting abi from routescan",
                extra={"contract_address": contract_address},
            )
            raise

        if data["status"] != "1":
            raise ChainException("Request to routescan failed: {}".format(data["result"]))

        abi = json.loads(data["result"])
        return abi

    async def get_block_for_timestamp_fallback(self, timestamp):
        query_params = {
            "module": "block",
            "action": "getblocknobytime",
            "timestamp": timestamp,
            "closest": "before",
        }
        url = f"{self._get_url()}?{urllib.parse.urlencode(query_params)}"
        data = await retry_get_json(url)
        result = int(data["result"])
        return result
