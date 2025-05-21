from chain_harvester.chain import Chain
from chain_harvester.mixins import EtherscanMixin


class ScrollMainnetChain(EtherscanMixin, Chain):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, chain="scroll", network="mainnet", **kwargs)
