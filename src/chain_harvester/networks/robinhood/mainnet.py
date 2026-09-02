from chain_harvester.chain import Chain
from chain_harvester.mixins import BlockscoutMixin


class RobinhoodMainnetChain(BlockscoutMixin, Chain):
    def __init__(self, *args, **kwargs):
        # No blockscout_url: Blockscout's hosted gateway (api.blockscout.com)
        # serves chain id 4663, so the mixin defaults to it, authenticated via
        # blockscout_api_key. The chain's self-hosted explorer
        # (robinhoodchain.blockscout.com) sits behind a Cloudflare bot
        # challenge that 403s every non-browser client.
        super().__init__(
            *args,
            chain="robinhood",
            network="mainnet",
            **kwargs,
        )
