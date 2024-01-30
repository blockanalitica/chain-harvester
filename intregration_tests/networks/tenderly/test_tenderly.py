from chain_harvester.networks.tenderly.testnet import TenderlyTestNetChain
from intregration_tests.env import API_KEYS, RPC_NODES
import os


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
