from chain_harvester.chain import Chain
from chain_harvester.mixins import OKLinkMixin


class XLayerMainnetChain(OKLinkMixin, Chain):
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            chain="xlayer",
            network="mainnet",
            oklink_chain_short_name="XLAYER",
            **kwargs,
        )
