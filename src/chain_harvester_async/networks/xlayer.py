from chain_harvester_async.chain import Chain
from chain_harvester_async.mixins import OKLinkMixin


class XLayerMainnetChain(OKLinkMixin, Chain):
    latest_block_offset = 30

    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            chain="xlayer",
            network="mainnet",
            oklink_chain_short_name="XLAYER",
            **kwargs,
        )
