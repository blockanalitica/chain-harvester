from chain_harvester.adapters.defillama import LLAMA_COINS_API_URL
from chain_harvester.chain import Chain
from chain_harvester.exceptions import ChainException
from chain_harvester.http import retry_get_json
from chain_harvester.mixins import EtherscanMixin


class BaseMainnetChain(EtherscanMixin, Chain):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, chain="base", network="mainnet", **kwargs)

    def get_block_for_timestamp_fallback(self, timestamp):
        url = f"{LLAMA_COINS_API_URL}block/{self.chain}/{timestamp}"
        block = retry_get_json(url, timeout=5)
        block_number = block["height"]
        block_timestamp = block["timestamp"]

        while block_timestamp > timestamp:
            if block_number == 0:
                raise ChainException(f"No {self.chain} block at or before {timestamp}")
            block_number -= 1
            block_timestamp = self.get_timestamp_for_block(block_number)

        return block_number
