from chain_harvester.networks.ethereum.mainnet import EthereumMainnetChain
from intregration_tests.env import ETHERSCAN_API_KEY, RPC_NODES


def test__call_contract_function():
    chain = EthereumMainnetChain(rpc=RPC_NODES["ethereum"]["mainnet"], api_key=ETHERSCAN_API_KEY)

    assert chain.rpc == RPC_NODES["ethereum"]["mainnet"]
    name = chain.call_contract_function("0x6b175474e89094c44da98b954eedeac495271d0f", "name")
    assert name == "Dai Stablecoin"


def test__yield_contract_events():
    chain = EthereumMainnetChain(rpc_nodes=RPC_NODES, api_key=ETHERSCAN_API_KEY)

    events = chain.yield_contract_events(
        "0x6b175474e89094c44da98b954eedeac495271d0f", "Transfer", from_block=17850969, to_block=17850974
    )

    assert len(list(events)) == 3


def test__yield_contract_events_by_topic():
    chain = EthereumMainnetChain(rpc_nodes=RPC_NODES, api_key=ETHERSCAN_API_KEY)

    events = chain.yield_contract_events_by_topic(
        "0x6b175474e89094c44da98b954eedeac495271d0f",
        ["0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"],
        from_block=17850969,
        to_block=17850974,
    )
    assert len(list(events)) == 3


def test__multicall():
    chain = EthereumMainnetChain(rpc_nodes=RPC_NODES)

    calls = []
    calls.append(
        (
            "0x6b175474e89094c44da98b954eedeac495271d0f",
            ["symbol()(string)"],
            ["symbol", None],
        )
    )
    calls.append(
        (
            "0x6b175474e89094c44da98b954eedeac495271d0f",
            ["name()(string)"],
            ["name", None],
        )
    )
    result = chain.multicall(calls)
    assert result["symbol"] == "DAI"
    assert result["name"] == "Dai Stablecoin"
