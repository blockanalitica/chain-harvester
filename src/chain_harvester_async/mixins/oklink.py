import json
import logging
import urllib.parse

from environs import env

from chain_harvester.exceptions import ChainException
from chain_harvester_async.adapters import defillama
from chain_harvester_async.mixins.base import BaseExplorerMixin
from chain_harvester_async.utils.http import retry_get_json

log = logging.getLogger(__name__)


class OKLinkMixin(BaseExplorerMixin):
    def __init__(self, oklink_chain_short_name=None, oklink_api_key=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.oklink_chain_short_name = oklink_chain_short_name
        self.oklink_api_key = oklink_api_key or env("OKLINK_API_KEY", None)
        self.oklink_url = "https://www.oklink.com/api/v5/explorer"

    async def get_abi_from_source(self, contract_address):
        query_params = {
            "chainShortName": self.oklink_chain_short_name,
            "contractAddress": contract_address,
        }
        query = urllib.parse.urlencode(query_params)
        url = f"{self.oklink_url}/contract/verify-contract-info?{query}"
        headers = {"Ok-Access-Key": self.oklink_api_key} if self.oklink_api_key else None

        try:
            data = await retry_get_json(url, headers=headers, timeout=5)
        except TimeoutError:
            log.exception(
                "Timeout when getting abi from oklink",
                extra={"contract_address": contract_address},
            )
            raise

        if data["code"] != "0" or not data["data"]:
            raise ChainException("Request to oklink failed: {}".format(data["msg"]))

        abi = json.loads(data["data"][0]["contractAbi"])
        return abi

    async def get_closest_block_before_timestamp(self, timestamp):
        return await defillama.get_closest_block_before_timestamp(self, timestamp)
