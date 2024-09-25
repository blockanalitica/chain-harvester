from chain_harvester.networks.linea.mainnet import LineaMainnetChain
from intregration_tests.env import API_KEYS, RPC_NODES


def test__multicall():
    chain = LineaMainnetChain(rpc_nodes=RPC_NODES, api_keys=API_KEYS)

    calls = []
    calls.append(
        (
            "0x4af15ec2a0bd43db75dd04e62faa3b8ef36b00d5",
            ["symbol()(string)"],
            ["symbol", None],
        )
    )
    calls.append(
        (
            "0x4af15ec2a0bd43db75dd04e62faa3b8ef36b00d5",
            ["name()(string)"],
            ["name", None],
        )
    )
    result = chain.multicall(calls)
    assert result["symbol"] == "DAI"
    assert result["name"] == "Dai Stablecoin"
