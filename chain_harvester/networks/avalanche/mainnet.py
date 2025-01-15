import logging

from chain_harvester.chain import Chain
from chain_harvester.constants import CHAINS

log = logging.getLogger(__name__)


class AvalancheMainnetChain(Chain):
    def __init__(
        self,
        rpc=None,
        rpc_nodes=None,
        api_key=None,
        api_keys=None,
        abis_path=None,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.chain = "avalanche"
        self.network = "mainnet"
        self.rpc = rpc or rpc_nodes[self.chain][self.network]
        self.chain_id = CHAINS[self.chain][self.network]
        self.abis_path = abis_path or "abis/avalanche/"
        self.api_key = None
        self.scan_url = "https://api.routescan.io/v2/network/mainnet/evm/43114/etherscan"
