from chain_harvester.adapters.alchemy import Alchemy
from chain_harvester.decoders import EventLogDecoder
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


def test_get_transactions_for_contracts__cowswap():
    alchemy = Alchemy("ethereum", "mainnet", rpc_nodes=RPC_NODES, api_keys=API_KEYS)
    data = alchemy.get_transactions_for_contracts(
        ["0x9008D19f58AAbD9eD0D60971565AA8510560ab41"],
        20427684,
        to_block=20427684 + 1,
        failed=False,
    )
    events = list(data)

    for log in events[0]["tx"]["logs"]:
        contract = alchemy.chain.get_contract("0x9008D19f58AAbD9eD0D60971565AA8510560ab41")
        data = EventLogDecoder(contract).decode_log(log)

    assert len(events) == 0
