from chain_harvester.chain import Chain
from chain_harvester.mixins import RoutescanMixin


class PlasmaMainnetChain(RoutescanMixin, Chain):
    latest_block_offset = 30

    def __init__(self, *args, **kwargs):
        super().__init__(*args, chain="plasma", network="mainnet", **kwargs)
