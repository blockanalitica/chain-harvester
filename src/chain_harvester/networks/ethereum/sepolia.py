from chain_harvester.chain import Chain
from chain_harvester.mixins import EtherscanMixin


class EthereumSepoliaChain(EtherscanMixin, Chain):
    latest_block_offset = 12

    def __init__(self, *args, **kwargs):
        super().__init__(*args, chain="ethereum", network="sepolia", **kwargs)
