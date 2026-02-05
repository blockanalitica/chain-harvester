import pytest
from environs import env

from chain_harvester_async.chain import Chain
from chain_harvester_async.mixins import EtherscanMixin

env.read_env()
# Constants need to be imported AFTER we read the env file as we use env variables
# in constants file


class DummyChain(EtherscanMixin, Chain):
    latest_block_offset = 50

    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            chain="ethereum",
            network="mainnet",
            abis_path="integration_tests/abis/ethereum/",
            step=5,
            **kwargs,
        )


@pytest.fixture
async def chain():
    chain = DummyChain()
    try:
        yield chain
    finally:
        await chain.aclose()
