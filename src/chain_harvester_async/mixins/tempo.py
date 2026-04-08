import logging

from chain_harvester.exceptions import ChainException
from chain_harvester_async.mixins.base import BaseExplorerMixin
from chain_harvester_async.utils.http import retry_get_json

log = logging.getLogger(__name__)


class TempoMixin(BaseExplorerMixin):
    def __init__(
        self,
        *args,
        **kwargs,
    ):
        self.api = "https://contracts.tempo.xyz/v2"
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
