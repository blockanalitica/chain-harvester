from chain_harvester_async.networks.tempo import TempoMainnetChain


async def test_multicall():
    async with TempoMainnetChain() as chain:
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


async def test_call_contract_function():
    async with TempoMainnetChain() as chain:
        share_price = await chain.call_contract_function(
            "0x891b473fe15ccce37827dde41f70d6ed4d607dfe", "getSharePrice"
        )
        assert share_price > 1
