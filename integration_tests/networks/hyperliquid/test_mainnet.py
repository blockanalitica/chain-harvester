from chain_harvester.networks.hyperliquid.mainnet import HyperliquidMainnetChain
from integration_tests.env import API_KEYS, RPC_NODES


def test__latest_block():
    chain = HyperliquidMainnetChain(rpc=RPC_NODES["hyperliquid"]["mainnet"], api_keys=API_KEYS)

    assert chain.rpc == RPC_NODES["hyperliquid"]["mainnet"]
    block = chain.get_latest_block()
    assert block is not None
    assert block > 0


# def test__call_contract_function():
#     chain = HyperliquidMainnetChain(rpc=RPC_NODES["hyperliquid"]["mainnet"], api_keys=API_KEYS)

#     assert chain.rpc == RPC_NODES["hyperliquid"]["mainnet"]
#     name = chain.call_contract_function("0xffaa4a3d97fe9107cef8a3f48c069f577ff76cc1", "name")
#     assert name == "Staked HYPE"


def test__multicall():
    chain = HyperliquidMainnetChain(rpc=RPC_NODES["hyperliquid"]["mainnet"], api_keys=API_KEYS)

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
    result = chain.multicall(calls)
    assert result["symbol"] == "stHYPE"
    assert result["name"] == "Staked HYPE"


def test__get_events_for_contract():
    chain = HyperliquidMainnetChain(rpc=RPC_NODES["hyperliquid"]["mainnet"], api_keys=API_KEYS)

    events = chain.get_events_for_contract(
        "0xffaa4a3d97fe9107cef8a3f48c069f577ff76cc1",
        from_block=1814581,
        to_block=1814681,
    )

    assert len(list(events)) == 14


def test__multicall_archive():
    chain = HyperliquidMainnetChain(rpc=RPC_NODES["hyperliquid"]["mainnet"], api_keys=API_KEYS)

    calls = []
    calls.append(
        (
            "0xffaa4a3d97fe9107cef8a3f48c069f577ff76cc1",
            ["totalSupplyRaw()(uint256)"],
            ["supply", None],
        )
    )
    result = chain.multicall(calls, block_identifier=1814581)
    assert result["supply"] == 3153934590558314965411152859903

    calls = []
    calls.append(
        (
            "0xffaa4a3d97fe9107cef8a3f48c069f577ff76cc1",
            ["totalSupplyRaw()(uint256)"],
            ["supply", None],
        )
    )
    result = chain.multicall(calls, block_identifier=1814681)
    assert result["supply"] == 3153935026734015671971104550724
