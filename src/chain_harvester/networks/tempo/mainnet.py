from chain_harvester.chain import Chain
from chain_harvester.mixins import TempoMixin


class ScrollMainnetChain(TempoMixin, Chain):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, chain="tempo", network="mainnet", **kwargs)
