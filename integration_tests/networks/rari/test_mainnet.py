import pytest

from chain_harvester.networks.rari.mainnet import RariMainnetChain


@pytest.fixture
async def rari_chain():
    chain = RariMainnetChain(
        abis_path="integration_tests/abis/rari/",
    )
    try:
        yield chain
    finally:
        await chain.aclose()


async def test_multicall(rari_chain):
    calls = [
        (
            "0x0cEe3e7DE0dA8DE7C82054E40F5fB4301685E908",
            ["symbol()(string)"],
            ["symbol", None],
        ),
        (
            "0x0cEe3e7DE0dA8DE7C82054E40F5fB4301685E908",
            ["name()(string)"],
            ["name", None],
        ),
    ]
    result = await rari_chain.multicall(calls)
    assert result["symbol"] == "WETH"
    assert result["name"] == "Wrapped Ether"
