from chain_harvester_async.networks import BaseMainnetChain, RobinhoodMainnetChain
from chain_harvester_async.networks.plume import PlumeMainnetChain

RPC = "http://localhost:1"


def test_robinhood_uses_hosted_gateway():
    # Regression guard: pinning blockscout_url to the chain's self-hosted
    # explorer made every lookup anonymous (the instance takes no API key)
    # and per-IP rate-limited. The hosted gateway serves chain id 4663
    # authenticated, so the chain must default to it.
    chain = RobinhoodMainnetChain(rpc=RPC, blockscout_api_key="test-key")
    assert chain.blockscout_url == "https://api.blockscout.com/4663/api"
    assert chain.headers == {"Authorization": "Bearer test-key"}


def test_base_uses_hosted_gateway():
    chain = BaseMainnetChain(rpc=RPC, blockscout_api_key="test-key")
    assert chain.blockscout_url == "https://api.blockscout.com/8453/api"
    assert chain.headers == {"Authorization": "Bearer test-key"}


def test_plume_stays_self_hosted():
    # The gateway does not serve Plume (98866: "Network not supported"), so
    # its self-hosted explorer stays pinned — and self-hosted means no auth.
    chain = PlumeMainnetChain(rpc=RPC, blockscout_api_key="test-key")
    assert chain.blockscout_url == "https://explorer.plume.org/api"
    assert chain.headers is None
