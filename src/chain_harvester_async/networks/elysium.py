from chain_harvester_async.chain import Chain
from chain_harvester_async.mixins import KinetiqMixin


class ElysiumMainnetChain(KinetiqMixin, Chain):
    latest_block_offset = 30

    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            chain="elysium",
            network="mainnet",
            kinetiq_url="https://elysium.kinetiq.xyz",
            **kwargs,
        )
