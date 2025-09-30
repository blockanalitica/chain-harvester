from chain_harvester.networks.plasma.mainnet import PlasmaMainnetChain
from integration_tests.env import RPC_NODES


def test__latest_block():
    chain = PlasmaMainnetChain(rpc=RPC_NODES["plasma"]["mainnet"])

    assert chain.rpc == RPC_NODES["plasma"]["mainnet"]
    block = chain.get_latest_block()
    assert block is not None
    assert block > 0
