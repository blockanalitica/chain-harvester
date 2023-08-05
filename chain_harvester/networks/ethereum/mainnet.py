import json
import logging

import requests

from chain_harvester.chain import Chain
from chain_harvester.constants import CHAINS

log = logging.getLogger(__name__)


class EthereumMainnetChain(Chain):
    def __init__(self, rpc=None, api_key=None, abis_path=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.chain = "ethereum"
        self.network = "mainnet"
        self.rpc = rpc
        self.chain_id = CHAINS[self.chain][self.network]
        self.step = 10_000
        self.abis_path = abis_path or "abis/"
        self.api_key = api_key

    def get_abi_from_source(self, contract_address):
        try:
            req = requests.get(
                "https://api.etherscan.io/api?module=contract&action=getabi&address="
                + contract_address
                + "&apikey="
                + self.api_key,
                timeout=5,
            )
        except requests.exceptions.Timeout:
            log.exception("Timeout when get abi from etherscan", extra={"contract_address": contract_address})
            raise
        resp = json.loads(req.text)
        abi = json.loads(resp["result"])
        return abi
