from chain_harvester_async.chain import Chain
from chain_harvester_async.mixins import EtherscanMixin


class BaseMainnetChain(EtherscanMixin, Chain):
    latest_block_offset = 30

    def __init__(self, *args, **kwargs):
        super().__init__(*args, chain="base", network="mainnet", **kwargs)
