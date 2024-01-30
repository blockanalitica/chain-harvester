import json
import logging

import requests

from chain_harvester.chain import Chain, ChainException
from chain_harvester.constants import CHAINS

log = logging.getLogger(__name__)


class TenderlyTestNetChain(Chain):
    def __init__(
        self, rpc=None, rpc_nodes=None, api_key=None, api_keys=None, abis_path=None, *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.chain = "tenderly"
        self.network = "testnet"
        self.rpc = rpc or rpc_nodes[self.chain][self.network]
        self.chain_id = CHAINS[self.chain][self.network]
        self.abis_path = abis_path or "abis/"
        self.api_key = api_key or api_keys[self.chain][self.network]

    def get_abi_source_url(self, contract_address):
        url = (
            "https://api.tenderly.co/api/v1/account/block-analitica/project/maker/testnet/28ebabca-6c78-4ae3-936c-4cec87e4e597/verified-contract/"
            + contract_address
        )
        return url

    def get_abi_from_source(self, contract_address):
        log.error("ABI for %s was fetched from etherscan. Add it to abis folder!", contract_address)
        try:
            response = requests.get(
                self.get_abi_source_url(contract_address),
                timeout=5,
                headers={"X-Access-Key": self.api_key},
            )
        except requests.exceptions.Timeout:
            log.exception(
                "Timeout when get abi from etherscan", extra={"contract_address": contract_address}
            )
            raise

        response.raise_for_status()
        data = response.json()

        abi = data["data"]["raw_abi"]
        return abi
