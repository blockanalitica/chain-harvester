from chain_harvester_async.chain import Chain
from chain_harvester_async.mixins import BlockscoutMixin


class ModeMainnetChain(BlockscoutMixin, Chain):
    latest_block_offset = 30

    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            chain="mode",
            network="mainnet",
            blockscout_url="https://explorer.mode.network",
            **kwargs,
        )
