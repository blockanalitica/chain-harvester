from chain_harvester.adapters.alchemy import Alchemy
from intregration_tests.env import API_KEYS, RPC_NODES


def test_get_block_transactions():
    alchemy = Alchemy("ethereum", "mainnet", rpc_nodes=RPC_NODES, api_keys=API_KEYS)
    data = alchemy.get_block_transactions(20192996)
    assert len(data) == 131


def test_get_transactions_for_contracts():
    alchemy = Alchemy("ethereum", "mainnet", rpc_nodes=RPC_NODES, api_keys=API_KEYS)
    data = alchemy.get_transactions_for_contracts(
        ["0x89B78CfA322F6C5dE0aBcEecab66Aee45393cC5A"], 20391781, to_block=20391781
    )
    events = list(data)
    assert len(events) == 1


def test_get_transactions_for_contracts__failed():
    alchemy = Alchemy("ethereum", "mainnet", rpc_nodes=RPC_NODES, api_keys=API_KEYS)
    data = alchemy.get_transactions_for_contracts(
        ["0x89B78CfA322F6C5dE0aBcEecab66Aee45393cC5A"],
        20391781,
        to_block=20391781,
        failed=True,
    )
    events = list(data)
    assert len(events) == 0
