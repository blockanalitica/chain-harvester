from chain_harvester.constants import MULTICALL3_ADDRESSES, Network
from chain_harvester.networks.robinhood.mainnet import RobinhoodMainnetChain
from integration_tests.env import RPC_NODES


def test_latest_block():
    chain = RobinhoodMainnetChain(rpc_nodes=RPC_NODES)

    assert chain.rpc == RPC_NODES["robinhood"]["mainnet"]
    block = chain.get_latest_block()
    assert block is not None
    assert block > 0


def test_multicall():
    chain = RobinhoodMainnetChain(rpc_nodes=RPC_NODES)

    multicall3 = MULTICALL3_ADDRESSES[Network.Robinhood]
    calls = [
        (multicall3, ["getChainId()(uint256)"], ["chain_id", None]),
        (multicall3, ["getBlockNumber()(uint256)"], ["block_number", None]),
    ]
    result = chain.multicall(calls)
    assert result["chain_id"] == Network.Robinhood
    assert result["block_number"] > 0
