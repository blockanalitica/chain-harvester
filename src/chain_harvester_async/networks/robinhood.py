from chain_harvester_async.chain import Chain
from chain_harvester_async.mixins import BlockscoutMixin


class RobinhoodMainnetChain(BlockscoutMixin, Chain):
    latest_block_offset = 30

    def __init__(self, *args, **kwargs):
        # No blockscout_url: Blockscout's hosted gateway (api.blockscout.com)
        # serves chain id 4663, so the mixin defaults to it, authenticated via
        # blockscout_api_key. The chain's self-hosted explorer
        # (robinhoodchain.blockscout.com) takes no API key and rate-limits
        # anonymous callers per IP, which 429s any backfill-paced usage.
        super().__init__(
            *args,
            chain="robinhood",
            network="mainnet",
            **kwargs,
        )
