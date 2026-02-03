from chain_harvester_async.chain import Chain
from chain_harvester_async.mixins import TenderlyMixin


class TenderlyTestnetChain(TenderlyMixin, Chain):
    latest_block_offset = 12

    def __init__(self, *args, **kwargs):
        super().__init__(*args, chain="tenderly", network="testnet", **kwargs)
