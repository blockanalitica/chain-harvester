from chain_harvester.chain import Chain
from chain_harvester.mixins import BlockscoutMixin


class HyperliquidMainnetChain(BlockscoutMixin, Chain):
    latest_block_offset = 30

    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            chain="hyperliquid",
            network="mainnet",
            blockscout_url="https://www.hyperscan.com",
            **kwargs,
        )
