from chain_harvester.adapters.alchemy_chain import AlchemyChain
from integration_tests.env import RPC_NODES


def test_batch_codes():
    alchemy = AlchemyChain("ethereum", rpc_nodes=RPC_NODES)
    data = alchemy.get_batch_codes(["0xe8e8f41ed29e46f34e206d7d2a7d6f735a3ff2cb"])
    assert data == [{"jsonrpc": "2.0", "id": 1, "result": "0x"}]
