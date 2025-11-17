import pytest

from chain_harvester.chain import Chain


class DummyChain(Chain):
    latest_block_offset = 50


@pytest.fixture
async def chain():
    return DummyChain(chain="ethereum", network="mainnet")


async def test_get_latest_block(chain):
    latest = await chain.get_latest_block()
    assert latest > 0
    assert isinstance(latest, int)


async def test_get_latest_block_offset(chain):
    latest = await chain.get_latest_block(offset=0)
    with_offset = await chain.get_latest_block(offset=100)
    # Test that offset is lower than the latest but not for full amount as there's delay
    # between the calls so it's not necessary that chain returns the same block number
    assert with_offset < latest - 90


async def test_get_block_info(chain):
    block = await chain.get_block_info(23696969)
    assert len(block.transactions) == 171
    assert block.number == 23696969
    assert (
        block.hash.to_0x_hex()
        == "0x7452a43b26b41f70df0c59e53f5bf447df8e9f5587d312b90e0aeafc9655b7e4"
    )
