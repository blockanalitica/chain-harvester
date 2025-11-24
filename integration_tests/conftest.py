import pytest
from environs import env

from chain_harvester.chain import Chain
from chain_harvester.mixins import EtherscanMixin

env.read_env()
# Constants need to be imported AFTER we read the env file as we use env variables
# in constants file
from integration_tests.constants import ETHERSCAN_API_KEY  # noqa: E402


class DummyChain(EtherscanMixin, Chain):
    latest_block_offset = 50

    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            chain="ethereum",
            network="mainnet",
            abis_path="integration_tests/abis/ethereum/",
            etherscan_api_key=ETHERSCAN_API_KEY,
            **kwargs,
        )


@pytest.fixture
async def chain():
    return DummyChain()
