import json
import logging

import requests

from chain_harvester.chain import Chain, ChainException
from chain_harvester.constants import CHAINS

log = logging.getLogger(__name__)


class GnosisMainnetChain(Chain):
    def __init__(
        self, rpc=None, rpc_nodes=None, api_key=None, api_keys=None, abis_path=None, *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.chain = "gnosis"
        self.network = "mainnet"
        self.rpc = rpc or rpc_nodes[self.chain][self.network]
        self.chain_id = CHAINS[self.chain][self.network]
        self.abis_path = abis_path or "abis/"
        self.api_key = api_key or api_keys[self.chain][self.network]

    def get_abi_from_source(self, contract_address):
        try:
            response = requests.get(
                "https://api.gnosisscan.io/api?module=contract&action=getabi&address="
                + contract_address
                + "&apikey="
                + self.api_key,
                timeout=5,
            )
        except requests.exceptions.Timeout:
            log.exception(
                "Timeout when get abi from gnosisscan", extra={"contract_address": contract_address}
            )
            raise

        response.raise_for_status()
        data = response.json()

        if data["status"] != "1":
            raise ChainException("Request to gnosisscan failed: {}".format(data["result"]))

        abi = json.loads(data["result"])
        return abi
