from integration_tests.constants import USDS_CONTRACT


async def test_multicall(chain):
    calls = []
    for x in range(50):
        calls.append(
            (
                USDS_CONTRACT,
                ["symbol()(string)"],
                [f"symbol{x}", None],
            )
        )
        calls.append(
            (
                USDS_CONTRACT,
                ["name()(string)"],
                [f"name{x}", None],
            )
        )
    result = await chain.multicall(calls)
    assert len(result) == 100
