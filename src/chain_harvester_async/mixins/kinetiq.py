import json
import logging
import urllib.parse

from chain_harvester.exceptions import ChainException
from chain_harvester_async.mixins.base import BaseExplorerMixin
from chain_harvester_async.utils.http import retry_get_json

log = logging.getLogger(__name__)


class KinetiqMixin(BaseExplorerMixin):
    def __init__(self, *args, kinetiq_url, **kwargs):
        super().__init__(*args, **kwargs)
        self.kinetiq_url = f"{kinetiq_url}/api"

    async def get_abi_from_source(self, contract_address):
        query_params = {
            "module": "contract",
            "action": "getabi",
            "address": contract_address,
        }
        url = f"{self.kinetiq_url}?{urllib.parse.urlencode(query_params)}"
        try:
            data = await retry_get_json(url, timeout=30)
        except TimeoutError:
            log.exception(
                "Timeout when getting abi from %s",
                self.kinetiq_url,
                extra={"contract_address": contract_address},
            )
            raise

        if data.get("status") != "1":
            raise ChainException(f"Request to {self.kinetiq_url} failed: {data.get('result')}")

        return json.loads(data["result"])

    async def get_closest_block_before_timestamp(self, timestamp):
        query_params = {
            "module": "block",
            "action": "getblocknobytime",
            "timestamp": timestamp,
            "closest": "before",
        }
        url = f"{self.kinetiq_url}?{urllib.parse.urlencode(query_params)}"
        try:
            data = await retry_get_json(url, timeout=30)
            return int(data["result"]["blockNumber"])
        except Exception:
            log.exception(
                "Failed to get closest block before %s from %s, searching from chain head",
                timestamp,
                self.kinetiq_url,
            )
            return await self.get_latest_block_number(offset=0)
