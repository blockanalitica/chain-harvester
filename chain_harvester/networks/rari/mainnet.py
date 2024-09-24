import logging

import requests

from chain_harvester.chain import Chain
from chain_harvester.constants import CHAINS

log = logging.getLogger(__name__)


class RariMainnetChain(Chain):
    def __init__(
        self, rpc=None, rpc_nodes=None, api_key=None, api_keys=None, abis_path=None, *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.chain = "rari"
        self.network = "mainnet"
        self.rpc = rpc or rpc_nodes[self.chain][self.network]
        self.chain_id = CHAINS[self.chain][self.network]
        self.abis_path = abis_path or f"abis/{self.chain}/{self.network}/"
        self.api_key = api_key or api_keys[self.chain][self.network]

    def get_abi_from_source(self, contract_address):
        log.error(
            "ABI for %s was fetched from rari.calderaexplorer.xyz. Add it to abis folder!",
            contract_address,
        )

        try:
            response = requests.get(
                f"https://rari.calderaexplorer.xyz/api/v2/smart-contracts/{contract_address}",
                timeout=5,
            )
        except requests.exceptions.Timeout:
            log.exception(
                "Timeout when get abi from rari.calderaexplorer.xyz",
                extra={"contract_address": contract_address},
            )
            raise

        response.raise_for_status()
        data = response.json()
        return data["abi"]
