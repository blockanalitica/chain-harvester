import json
import logging

import requests

from chain_harvester.chain import Chain
from chain_harvester.constants import CHAINS

log = logging.getLogger(__name__)


class FilecoinMainnetChain(Chain):
    def __init__(
        self, rpc=None, rpc_nodes=None, api_key=None, api_keys=None, abis_path=None, *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.chain = "filecoin"
        self.network = "mainnet"
        self.rpc = rpc or rpc_nodes[self.chain][self.network]
        self.chain_id = CHAINS[self.chain][self.network]
        self.abis_path = abis_path or "abis/filecoin/"
        self.api_key = api_key or api_keys[self.chain][self.network]

    def get_abi_from_source(self, contract_address):
        log.error("ABI for %s was fetched from filfox. Add it to abis folder!", contract_address)

        try:
            response = requests.get(
                f"https://filfox.info/api/v1/address/{contract_address}/contract",
                timeout=5,
            )
        except requests.exceptions.Timeout:
            log.exception(
                "Timeout when get abi from filfox", extra={"contract_address": contract_address}
            )
            raise

        response.raise_for_status()
        data = response.json()

        abi = json.loads(data["abi"])
        return abi
