import os

from chain_harvester.networks.tenderly.testnet import TenderlyTestNetChain
from intregration_tests.env import API_KEYS, RPC_NODES


def test__get_events_for_contract():
    chain = TenderlyTestNetChain(
        rpc_nodes=RPC_NODES,
        api_keys=API_KEYS,
        account=os.environ.get("TENDERLY_ACCOUNT"),
        project=os.environ.get("TENDERLY_PROJECT"),
        testnet_id=os.environ.get("TENDERLY_TESTNET_ID"),
    )
    events = chain.get_events_for_contract(
        "0x8b342f4ddcc71af65e4d2da9cd00cc0e945cfd12",
        from_block=19062236,
        to_block=19062238,
    )
    assert len(list(events)) == 1


def test_abi_to_event_topics():
    chain = TenderlyTestNetChain(
        rpc_nodes=RPC_NODES,
        api_keys=API_KEYS,
        account=os.environ.get("TENDERLY_ACCOUNT"),
        project=os.environ.get("TENDERLY_PROJECT"),
        testnet_id=os.environ.get("TENDERLY_TESTNET_ID"),
    )
    topics = chain.abi_to_event_topics("0x8b342f4ddcc71af65e4d2da9cd00cc0e945cfd12")
    assert len(topics) == 2
    topics = chain.abi_to_event_topics(
        "0x8b342f4ddcc71af65e4d2da9cd00cc0e945cfd12", events=["MkrToNgt"]
    )
    assert len(topics) == 1
    topics = chain.abi_to_event_topics(
        "0x8b342f4ddcc71af65e4d2da9cd00cc0e945cfd12", ignore=["MkrToNgt"]
    )
    assert len(topics) == 1
