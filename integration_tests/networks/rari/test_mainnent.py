from chain_harvester.networks.rari.mainnet import RariMainnetChain
from integration_tests.env import API_KEYS, RPC_NODES


def test__multicall():
    chain = RariMainnetChain(rpc_nodes=RPC_NODES, api_keys=API_KEYS)

    calls = []
    calls.append(
        (
            "0x0cEe3e7DE0dA8DE7C82054E40F5fB4301685E908",
            ["symbol()(string)"],
            ["symbol", None],
        )
    )
    calls.append(
        (
            "0x0cEe3e7DE0dA8DE7C82054E40F5fB4301685E908",
            ["name()(string)"],
            ["name", None],
        )
    )
    result = chain.multicall(calls)
    assert result["symbol"] == "WETH"
    assert result["name"] == "Wrapped Ether"
