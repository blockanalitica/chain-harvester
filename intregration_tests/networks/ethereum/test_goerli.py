from chain_harvester.networks.ethereum.goerli import EthereumGoerliChain
from intregration_tests.env import API_KEYS, RPC_NODES


def test__call_contract_function():
    chain = EthereumGoerliChain(rpc=RPC_NODES["ethereum"]["goerli"], api_keys=API_KEYS)
    assert chain.rpc == RPC_NODES["ethereum"]["goerli"]
    name = chain.call_contract_function("0x11fe4b6ae13d2a6055c8d9cf65c55bac32b5d844", "name")
    assert name == "Dai Stablecoin"


def test__get_events_for_contract():
    chain = EthereumGoerliChain(rpc_nodes=RPC_NODES, api_keys=API_KEYS)
    events = chain.get_events_for_contract(
        "0x11fe4b6ae13d2a6055c8d9cf65c55bac32b5d844",
        from_block=9544128,
        to_block=9544600,
    )
    assert len(list(events)) == 7


def test__get_events_for_contract_topics():
    chain = EthereumGoerliChain(rpc_nodes=RPC_NODES, api_keys=API_KEYS)
    events = chain.get_events_for_contract_topics(
        "0x11fe4b6ae13d2a6055c8d9cf65c55bac32b5d844",
        ["0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"],
        from_block=9544128,
        to_block=9544600,
    )
    assert len(list(events)) == 4


def test__multicall():
    chain = EthereumGoerliChain(rpc_nodes=RPC_NODES, api_keys=API_KEYS)

    calls = []
    calls.append(
        (
            "0x11fe4b6ae13d2a6055c8d9cf65c55bac32b5d844",
            ["symbol()(string)"],
            ["symbol", None],
        )
    )
    calls.append(
        (
            "0x11fe4b6ae13d2a6055c8d9cf65c55bac32b5d844",
            ["name()(string)"],
            ["name", None],
        )
    )
    result = chain.multicall(calls)
    assert result["symbol"] == "DAI"
    assert result["name"] == "Dai Stablecoin"
