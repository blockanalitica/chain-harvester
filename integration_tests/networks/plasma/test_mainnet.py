from chain_harvester.networks.plasma.mainnet import PlasmaMainnetChain
from integration_tests.env import RPC_NODES


def test_latest_block():
    chain = PlasmaMainnetChain(rpc_nodes=RPC_NODES)

    assert chain.rpc == RPC_NODES["plasma"]["mainnet"]
    block = chain.get_latest_block()
    assert block is not None
    assert block > 0
