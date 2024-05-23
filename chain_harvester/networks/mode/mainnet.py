import logging

import requests

from chain_harvester.chain import Chain
from chain_harvester.constants import CHAINS

log = logging.getLogger(__name__)


class ModeMainnetChain(Chain):
    def __init__(
        self, rpc=None, rpc_nodes=None, api_key=None, api_keys=None, abis_path=None, *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.chain = "mode"
        self.network = "mainnet"
        self.rpc = rpc or rpc_nodes[self.chain][self.network]
        self.chain_id = CHAINS[self.chain][self.network]
        self.abis_path = abis_path or "abis/mode/"
        self.api_key = api_key or api_keys[self.chain][self.network]

    def get_abi_from_source(self, contract_address):
        log.error(
            "ABI for %s was fetched from explorer.mode.network. Add it to abis folder!",
            contract_address,
        )
        url = f"https://explorer.mode.network/api/v2/smart-contracts/{contract_address}"
        try:
            response = requests.get(
                url,
                timeout=5,
            )
        except requests.exceptions.Timeout:
            log.exception(
                "Timeout when get abi from explorer.mode.network",
                extra={"contract_address": contract_address},
            )
            raise

        response.raise_for_status()
        data = response.json()
        return data["abi"]
