from chain_harvester.networks.tempo.mainnet import TempoMainnetChain
from integration_tests.env import RPC_NODES


async def test_multicall():
    chain = TempoMainnetChain(rpc_nodes=RPC_NODES)

    calls = []
    calls.append(
        (
            "0x891b473fe15ccce37827dde41f70d6ed4d607dfe",
            ["shareDecimals()(int)"],
            ["shareDecimals", None],
        )
    )
    calls.append(
        (
            "0x891b473fe15ccce37827dde41f70d6ed4d607dfe",
            ["shareUnit()(int)"],
            ["shareUnit", None],
        )
    )
    result = chain.multicall(calls)
    assert len(result) == 2


async def test_call_contract_function():
    chain = TempoMainnetChain(rpc_nodes=RPC_NODES)

    share_price = chain.call_contract_function(
        "0x891b473fe15ccce37827dde41f70d6ed4d607dfe", "getSharePrice"
    )
    assert share_price > 1
