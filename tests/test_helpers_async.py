import pytest
from chain_harvester.exceptions import ConfigError
from chain_harvester_async.helpers import get_chain

RPC_NODES = {
    "ethereum": {
        "mainnet": "http://localhost:8545",
    },
}


async def test_get_chain(monkeypatch):
    """Covers RPC node lookup and missing-config error handling."""
    monkeypatch.delenv("ETHEREUM_MAINNET_RPC", None)

    chain = get_chain("ethereum", rpc_nodes=RPC_NODES)
    assert chain.chain == "ethereum"

    chain = get_chain("ethereum", rpc=RPC_NODES["ethereum"]["mainnet"])
    assert chain.chain == "ethereum"

    with pytest.raises(ConfigError):
        chain = get_chain("ethereum")
        assert chain.chain == "ethereum"
