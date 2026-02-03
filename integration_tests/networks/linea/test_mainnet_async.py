import pytest

from chain_harvester_async.networks.linea import LineaMainnetChain


@pytest.fixture
async def linea_chain():
    chain = LineaMainnetChain(
        abis_path="integration_tests/abis/linea/",
    )
    try:
        yield chain
    finally:
        await chain.aclose()


async def test_multicall(linea_chain):
    calls = [
        (
            "0x4af15ec2a0bd43db75dd04e62faa3b8ef36b00d5",
            ["symbol()(string)"],
            ["symbol", None],
        ),
        (
            "0x4af15ec2a0bd43db75dd04e62faa3b8ef36b00d5",
            ["name()(string)"],
            ["name", None],
        ),
    ]
    result = await linea_chain.multicall(calls)
    assert result["symbol"] == "DAI"
    assert result["name"] == "Dai Stablecoin"
