import os

import pytest

from chain_harvester_async.networks.tenderly import TenderlyTestnetChain


@pytest.fixture
async def t_chain():
    chain = TenderlyTestnetChain(
        account=os.environ.get("TENDERLY_ACCOUNT"),
        project=os.environ.get("TENDERLY_PROJECT"),
        testnet_id=os.environ.get("TENDERLY_TESTNET_ID"),
    )
    try:
        yield chain
    finally:
        await chain.aclose()


@pytest.mark.skip(reason="Only for manual testing")
async def test_get_events_for_contract(t_chain):
    events = t_chain.get_events_for_contract(
        "0x8b342f4ddcc71af65e4d2da9cd00cc0e945cfd12",
        from_block=19062236,
        to_block=19062238,
    )
    assert len(list(events)) == 1


@pytest.mark.skip(reason="Only for manual testing")
async def test_abi_to_event_topics(t_chain):
    topics = t_chain.abi_to_event_topics("0x8b342f4ddcc71af65e4d2da9cd00cc0e945cfd12")
    assert len(topics) == 2
    topics = t_chain.abi_to_event_topics(
        "0x8b342f4ddcc71af65e4d2da9cd00cc0e945cfd12", events=["MkrToNgt"]
    )
    assert len(topics) == 1
    topics = t_chain.abi_to_event_topics(
        "0x8b342f4ddcc71af65e4d2da9cd00cc0e945cfd12", ignore=["MkrToNgt"]
    )
    assert len(topics) == 1
