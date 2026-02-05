import json
import logging

from chain_harvester_async.mixins.base import BaseExplorerMixin
from chain_harvester_async.utils.http import retry_get_json

log = logging.getLogger(__name__)


class FilfoxMixin(BaseExplorerMixin):
    async def get_abi_from_source(self, contract_address):
        log.error(
            "ABI for %s was fetched from filfox. Add it to abis folder!",
            contract_address,
        )

        try:
            data = await retry_get_json(
                f"https://filfox.info/api/v1/address/{contract_address}/contract",
                timeout=5,
            )
        except TimeoutError:
            log.exception(
                "Timeout when get abi from filfox",
                extra={"contract_address": contract_address},
            )
            raise

        abi = json.loads(data["abi"])
        return abi

    async def get_block_for_timestamp_fallback(self, timestamp):
        """
        Filfox API does not support fetching blocks by timestamp.
        Implemented to satisfy mixin interface.
        """
        raise NotImplementedError(
            "FilfoxMixin: fetching a block by timestamp is not supported by Filfox API"
        )
