import pytest

from chain_harvester_async.networks import GnosisMainnetChain


@pytest.fixture
async def gnosis_chain():
    chain = GnosisMainnetChain(
        abis_path="integration_tests/abis/gnosis/",
    )
    try:
        yield chain
    finally:
        await chain.aclose()


async def test_call_contract_function(gnosis_chain):
    name = await gnosis_chain.call_contract_function(
        "0xe91d153e0b41518a2ce8dd3d7944fa863463a97d", "name"
    )
    assert name == "Wrapped XDAI"


async def test_get_events_for_contract(gnosis_chain):
    events = gnosis_chain.get_events_for_contract(
        "0xe91d153e0b41518a2ce8dd3d7944fa863463a97d",
        from_block=29718440,
        to_block=29718445,
    )
    assert len([e async for e in events]) == 10


async def test_get_events_for_contract_topics(gnosis_chain):
    events = gnosis_chain.get_events_for_contract_topics(
        "0xe91d153e0b41518a2ce8dd3d7944fa863463a97d",
        ["0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"],
        from_block=29718440,
        to_block=29718445,
    )
    assert len([e async for e in events]) == 6


async def test_multicall(gnosis_chain):
    calls = [
        (
            "0xe91d153e0b41518a2ce8dd3d7944fa863463a97d",
            ["symbol()(string)"],
            ["symbol", None],
        ),
        (
            "0xe91d153e0b41518a2ce8dd3d7944fa863463a97d",
            ["name()(string)"],
            ["name", None],
        ),
    ]
    result = await gnosis_chain.multicall(calls)
    assert result["symbol"] == "WXDAI"
    assert result["name"] == "Wrapped XDAI"


async def test_multicall_history(gnosis_chain):
    calls = [
        (
            "0xe91d153e0b41518a2ce8dd3d7944fa863463a97d",
            [
                "balanceOf(address)(uint256)",
                "0xe91d153e0b41518a2ce8dd3d7944fa863463a97d",
            ],
            ["balanceOf", None],
        )
    ]

    result = await gnosis_chain.multicall(calls, block_identifier=29719907)
    assert result["balanceOf"] == 17779092364971360576215

    calls = [
        (
            "0xe91d153e0b41518a2ce8dd3d7944fa863463a97d",
            [
                "balanceOf(address)(uint256)",
                "0xe91d153e0b41518a2ce8dd3d7944fa863463a97d",
            ],
            ["balanceOf", None],
        )
    ]

    result = await gnosis_chain.multicall(calls, block_identifier=27719907)
    assert result["balanceOf"] == 17766592364971360576215
