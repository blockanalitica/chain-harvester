from chain_harvester.chain import Chain
from chain_harvester.mixins import BlockscoutMixin


class RobinhoodMainnetChain(BlockscoutMixin, Chain):
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            chain="robinhood",
            network="mainnet",
            blockscout_url="https://robinhoodchain.blockscout.com",
            **kwargs,
        )
