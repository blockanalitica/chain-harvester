from unittest.mock import AsyncMock, patch

import pytest

from chain_harvester.exceptions import ChainException
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


async def test_get_abi_from_source_sends_auth_and_lowercases():
    chain = RobinhoodMainnetChain(rpc=RPC, blockscout_api_key="test-key")
    with patch(
        "chain_harvester_async.mixins.blockscout.retry_get_json",
        AsyncMock(return_value={"abi": [1]}),
    ) as m:
        assert await chain.get_abi_from_source("0xABC") == [1]
    m.assert_awaited_once_with(
        "https://api.blockscout.com/4663/api/v2/smart-contracts/0xabc",
        headers={"Authorization": "Bearer test-key"},
        timeout=45,
    )


async def test_get_abi_from_source_raises_when_abi_missing():
    # An unverified contract comes back 200 with bytecode and no `abi` key; so does
    # an unauthenticated gateway response ({"error": "Proceed with API key ..."}).
    chain = RobinhoodMainnetChain(rpc=RPC, blockscout_api_key="test-key")
    with (
        patch(
            "chain_harvester_async.mixins.blockscout.retry_get_json",
            AsyncMock(return_value={"proxy_type": None, "implementations": []}),
        ),
        pytest.raises(ChainException),
    ):
        await chain.get_abi_from_source("0xabc")


async def test_missing_abi_does_not_re_raise_the_ambient_exception():
    # Regression guard: this branch used to be a bare `raise`, which re-raised
    # whatever was being handled further up — the S3 NoSuchKey that `_handle_abi_s3`
    # is inside when it falls back to the explorer — reporting an S3 miss for what
    # is really an unverified contract.
    chain = RobinhoodMainnetChain(rpc=RPC, blockscout_api_key="test-key")

    def s3_miss():
        raise RuntimeError("the S3 miss being handled")

    async def under_ambient_exception():
        try:
            s3_miss()
        except RuntimeError:
            return await chain.get_abi_from_source("0xabc")

    with (
        patch(
            "chain_harvester_async.mixins.blockscout.retry_get_json",
            AsyncMock(return_value={}),
        ),
        pytest.raises(ChainException),
    ):
        await under_ambient_exception()
