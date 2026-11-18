import logging

from chain_harvester_async.chain import Chain
from chain_harvester_async.mixins import KinetiqMixin

log = logging.getLogger(__name__)


class ElysiumMainnetChain(KinetiqMixin, Chain):
    latest_block_offset = 30

    def __init__(self, *args, **kwargs):
        if kwargs.pop("use_hypersync", False):
            log.warning("Hypersync is not supported on Elysium, using RPC instead")
        kwargs.pop("hypersync_api_key", None)
        super().__init__(
            *args,
            chain="elysium",
            network="mainnet",
            kinetiq_url="https://elysium.kinetiq.xyz",
            use_hypersync=False,
            **kwargs,
        )
