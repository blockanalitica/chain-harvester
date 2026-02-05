from chain_harvester_async.chain import Chain
from chain_harvester_async.mixins import EtherscanMixin


class EthereumMainnetChain(EtherscanMixin, Chain):
    latest_block_offset = 12

    def __init__(self, *args, **kwargs):
        super().__init__(*args, chain="ethereum", network="mainnet", **kwargs)


class EthereumSepoliaChain(EtherscanMixin, Chain):
    latest_block_offset = 12

    def __init__(self, *args, **kwargs):
        super().__init__(*args, chain="ethereum", network="sepolia", **kwargs)
