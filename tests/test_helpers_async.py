from unittest.mock import Mock, sentinel

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


def test_get_elysium_chain_uses_hypersync_when_enabled(monkeypatch, tmp_path):
    config = Mock()
    client = Mock()
    monkeypatch.setattr("chain_harvester_async.chain.ClientConfig", config)
    monkeypatch.setattr("chain_harvester_async.chain.HypersyncClient", client)

    chain = get_chain(
        "elysium",
        rpc="http://localhost:8545",
        abis_path=tmp_path,
        use_hypersync=True,
        hypersync_api_key=sentinel.api_key,
    )

    assert chain.use_hypersync
    config.assert_called_once_with(url="https://99901.hypersync.xyz", api_token=sentinel.api_key)
    client.assert_called_once_with(config.return_value)


def test_get_elysium_chain_uses_rpc_by_default(tmp_path):
    chain = get_chain("elysium", rpc="http://localhost:8545", abis_path=tmp_path)

    assert not chain.use_hypersync
