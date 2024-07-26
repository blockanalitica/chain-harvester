import types

from chain_harvester.api import get_events_for_contracts, get_transactions_for_contracts
from intregration_tests.env import API_KEYS, RPC_NODES


def test_get_transactions_for_contracts():
    config = {
        "rpc": RPC_NODES["ethereum"]["mainnet"],
        "etherscan_api_key": API_KEYS["ethereum"]["mainnet"],
    }
    data = get_transactions_for_contracts(
        "ethereum",
        ["0x89B78CfA322F6C5dE0aBcEecab66Aee45393cC5A"],
        20391781,
        to_block=20391781,
        config=config,
    )
    assert isinstance(data, types.GeneratorType)

    assert len(list(data)) == 1


def test_get_transactions_for_contracts__failed():
    config = {
        "rpc": RPC_NODES["ethereum"]["mainnet"],
        "etherscan_api_key": API_KEYS["ethereum"]["mainnet"],
    }
    data = get_transactions_for_contracts(
        "ethereum",
        ["0x89B78CfA322F6C5dE0aBcEecab66Aee45393cC5A"],
        20391781,
        to_block=20391781,
        failed=True,
        config=config,
    )
    assert isinstance(data, types.GeneratorType)

    assert len(list(data)) == 0


def test_get_events_for_contracts():
    config = {
        "rpc": RPC_NODES["ethereum"]["mainnet"],
        "etherscan_api_key": API_KEYS["ethereum"]["mainnet"],
    }
    events = get_events_for_contracts(
        "ethereum",
        ["0x6b175474e89094c44da98b954eedeac495271d0f"],
        ["0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"],
        from_block=17850969,
        to_block=17850974,
        config=config,
    )
    assert isinstance(events, types.GeneratorType)
    assert len(list(events)) == 3
