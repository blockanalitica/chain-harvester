import pytest

from chain_harvester_async.networks import RobinhoodMainnetChain


@pytest.fixture
async def robinhood_chain():
    chain = RobinhoodMainnetChain(
        abis_path="integration_tests/abis/robinhood/",
    )
    async with chain as c:
        yield c


async def test_latest_block(robinhood_chain):
    block = await robinhood_chain.get_latest_block_number()
    assert block is not None
    assert block > 0
