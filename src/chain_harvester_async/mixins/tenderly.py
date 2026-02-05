import logging

from chain_harvester_async.mixins.base import BaseExplorerMixin
from chain_harvester_async.utils.http import retry_get_json

log = logging.getLogger(__name__)


class TenderlyMixin(BaseExplorerMixin):
    def __init__(
        self,
        account,
        project,
        testnet_id,
        api_key,
        *args,
        **kwargs,
    ):
        self.account = account
        self.project = project
        self.testnet_id = testnet_id
        self.api_key = api_key
        super().__init__(*args, **kwargs)

    async def get_abi_from_source(self, contract_address):
        log.error(
            "ABI for %s was fetched from tenderly. Add it to abis folder!",
            contract_address,
        )

        url = (
            "https://api.tenderly.co/api/v1/"
            f"account/{self.account}/project/{self.project}/testnet/{self.testnet_id}/"
            f"verified-contract/{contract_address}"
        )
        try:
            data = await retry_get_json(
                url=url,
                timeout=5,
                headers={"X-Access-Key": self.api_key},
            )
        except TimeoutError:
            log.exception(
                "Timeout when get abi from tenderly",
                extra={"contract_address": contract_address},
            )
            raise

        abi = data["data"]["raw_abi"]
        return abi
