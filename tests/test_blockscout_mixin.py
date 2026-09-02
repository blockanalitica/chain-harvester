from unittest.mock import patch

import pytest

from chain_harvester.exceptions import ChainException
from chain_harvester.networks.plume.mainnet import PlumeMainnetChain
from chain_harvester.networks.robinhood.mainnet import RobinhoodMainnetChain

RPC = "http://localhost:1"


def test_robinhood_uses_hosted_gateway(tmp_path):
    # Regression guard: the self-hosted explorer sits behind a Cloudflare bot
    # challenge and 403s every request from a non-browser client.
    chain = RobinhoodMainnetChain(rpc=RPC, blockscout_api_key="test-key", abis_path=tmp_path)
    assert chain.blockscout_url == "https://api.blockscout.com/4663/api"
    assert chain.headers == {"Authorization": "Bearer test-key"}


def test_plume_stays_self_hosted(tmp_path):
    chain = PlumeMainnetChain(rpc=RPC, blockscout_api_key="test-key", abis_path=tmp_path)
    assert chain.blockscout_url == "https://explorer.plume.org/api"
    assert chain.headers is None


def test_get_abi_from_source_sends_auth_and_lowercases(tmp_path):
    chain = RobinhoodMainnetChain(rpc=RPC, blockscout_api_key="test-key", abis_path=tmp_path)
    with patch("chain_harvester.mixins.retry_get_json", return_value={"abi": [1]}) as m:
        assert chain.get_abi_from_source("0xABC") == [1]
    m.assert_called_once_with(
        "https://api.blockscout.com/4663/api/v2/smart-contracts/0xabc",
        headers={"Authorization": "Bearer test-key"},
        timeout=15,
    )


def test_get_abi_from_source_raises_when_abi_missing(tmp_path):
    chain = RobinhoodMainnetChain(rpc=RPC, blockscout_api_key="test-key", abis_path=tmp_path)
    with (
        patch("chain_harvester.mixins.retry_get_json", return_value={"message": "nope"}),
        pytest.raises(ChainException),
    ):
        chain.get_abi_from_source("0xabc")
