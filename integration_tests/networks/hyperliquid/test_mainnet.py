import pytest

from chain_harvester.networks.hyperliquid.mainnet import HyperliquidMainnetChain


@pytest.fixture
async def hype_chain():
    chain = HyperliquidMainnetChain(
        abis_path="integration_tests/abis/hyperliquid/",
    )
    try:
        yield chain
    finally:
        await chain.aclose()


async def test_latest_block(hype_chain):
    block = await hype_chain.get_latest_block()
    assert block is not None
    assert block > 0


async def test_get_events_for_contract(hype_chain):
    events = hype_chain.get_events_for_contract(
        "0x5555555555555555555555555555555555555555",
        from_block=1814581,
        to_block=1814590,
    )
    assert len([e async for e in events]) == 21


async def test_multicall(hype_chain):
    calls = [
        (
            "0xffaa4a3d97fe9107cef8a3f48c069f577ff76cc1",
            ["symbol()(string)"],
            ["symbol", None],
        ),
        (
            "0xffaa4a3d97fe9107cef8a3f48c069f577ff76cc1",
            ["name()(string)"],
            ["name", None],
        ),
    ]
    result = await hype_chain.multicall(calls)
    assert result["symbol"] == "stHYPE"
    assert result["name"] == "Staked HYPE"


async def test_multicall_archive(hype_chain):
    calls = [
        (
            "0xffaa4a3d97fe9107cef8a3f48c069f577ff76cc1",
            ["totalSupplyRaw()(uint256)"],
            ["supply", None],
        )
    ]
    result = await hype_chain.multicall(calls, block_identifier=1814581)
    assert result["supply"] == 3153934590558314965411152859903

    calls = [
        (
            "0xffaa4a3d97fe9107cef8a3f48c069f577ff76cc1",
            ["totalSupplyRaw()(uint256)"],
            ["supply", None],
        )
    ]
    result = await hype_chain.multicall(calls, block_identifier=1814681)
    assert result["supply"] == 3153935026734015671971104550724
