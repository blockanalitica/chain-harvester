import pytest
from chain_harvester.networks.hyperliquid.mainnet import HyperliquidMainnetChain
from integration_tests.env import RPC_NODES


@pytest.fixture
def hyperliquid_chain():
    chain = HyperliquidMainnetChain(
        rpc=RPC_NODES["hyperliquid"]["mainnet"],
    )
    return chain


def test_latest_block(hyperliquid_chain):
    assert hyperliquid_chain.rpc == RPC_NODES["hyperliquid"]["mainnet"]
    block = hyperliquid_chain.get_latest_block()
    assert block is not None
    assert block > 0


def test_multicall(hyperliquid_chain):
    calls = []
    calls.append(
        (
            "0xffaa4a3d97fe9107cef8a3f48c069f577ff76cc1",
            ["symbol()(string)"],
            ["symbol", None],
        )
    )
    calls.append(
        (
            "0xffaa4a3d97fe9107cef8a3f48c069f577ff76cc1",
            ["name()(string)"],
            ["name", None],
        )
    )
    result = hyperliquid_chain.multicall(calls)
    assert result["symbol"] == "stHYPE"
    assert result["name"] == "Staked HYPE"


def test_get_events_for_contract(hyperliquid_chain):
    events = hyperliquid_chain.get_events_for_contract(
        "0x5555555555555555555555555555555555555555",
        from_block=1814581,
        to_block=1814590,
    )

    assert len(list(events)) == 21


def test_multicall_archive(hyperliquid_chain):
    calls = []
    calls.append(
        (
            "0xffaa4a3d97fe9107cef8a3f48c069f577ff76cc1",
            ["totalSupplyRaw()(uint256)"],
            ["supply", None],
        )
    )
    result = hyperliquid_chain.multicall(calls, block_identifier=1814581)
    assert result["supply"] == 3153934590558314965411152859903

    calls = []
    calls.append(
        (
            "0xffaa4a3d97fe9107cef8a3f48c069f577ff76cc1",
            ["totalSupplyRaw()(uint256)"],
            ["supply", None],
        )
    )
    result = hyperliquid_chain.multicall(calls, block_identifier=1814681)
    assert result["supply"] == 3153935026734015671971104550724
