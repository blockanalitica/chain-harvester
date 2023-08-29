from chain_harvester.networks.ethereum.goerli import EthereumGoerliChain
from intregration_tests.env import ETHERSCAN_API_KEY, RPC_NODES


def test__call_contract_function():
    chain = EthereumGoerliChain(rpc=RPC_NODES["ethereum"]["goerli"], api_key=ETHERSCAN_API_KEY)
    assert chain.rpc == RPC_NODES["ethereum"]["goerli"]
    name = chain.call_contract_function("0x11fe4b6ae13d2a6055c8d9cf65c55bac32b5d844", "name")
    assert name == "Dai Stablecoin"


def test__yield_contract_events():
    chain = EthereumGoerliChain(rpc_nodes=RPC_NODES, api_key=ETHERSCAN_API_KEY)
    events = chain.yield_contract_events(
        "0x11fe4b6ae13d2a6055c8d9cf65c55bac32b5d844",
        "Transfer",
        from_block=9544128,
        to_block=9544600,
    )
    assert len(list(events)) == 4


def test__yield_contract_events_by_topic():
    chain = EthereumGoerliChain(rpc_nodes=RPC_NODES, api_key=ETHERSCAN_API_KEY)
    events = chain.yield_contract_events_by_topic(
        "0x11fe4b6ae13d2a6055c8d9cf65c55bac32b5d844",
        ["0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"],
        from_block=9544128,
        to_block=9544600,
    )
    assert len(list(events)) == 4


def test__multicall():
    chain = EthereumGoerliChain(rpc_nodes=RPC_NODES)

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
