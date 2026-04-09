from chain_harvester_async.networks.tempo import TempoMainnetChain


async def test_multicall():
    chain = TempoMainnetChain()

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
    result = await chain.multicall(calls)
    assert len(result) == 2

    await chain.aclose()


async def test_call_contract_function():
    chain = TempoMainnetChain()

    share_price = await chain.call_contract_function(
        "0x891b473fe15ccce37827dde41f70d6ed4d607dfe", "getSharePrice"
    )
    assert share_price > 1

    await chain.aclose()
