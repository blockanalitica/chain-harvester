import pytest

from chain_harvester_async.networks.plasma import PlasmaMainnetChain


@pytest.fixture
async def plasma_chain():
    chain = PlasmaMainnetChain(
        abis_path="integration_tests/abis/plasma/",
    )
    try:
        yield chain
    finally:
        await chain.aclose()


async def test_latest_block(plasma_chain):
    block = await plasma_chain.get_latest_block()
    assert block is not None
    assert block > 0
