from unittest.mock import AsyncMock, patch

import pytest
from web3 import Web3

from chain_harvester_async.networks import RobinhoodMainnetChain

RPC = "http://localhost:1"
VAULT = "0x19D55F7Fe2d3962796F5825cbdaE2dD493Be0986"
SAMPLE_ABI = [{"type": "event", "name": "Deposit", "inputs": [], "anonymous": False}]


@pytest.mark.asyncio
async def test__register_abi__skips_lookup():
    # A registered ABI must be served from the cache without touching local
    # storage, S3, or the explorer — the whole point is that the explorer may
    # not have matched the contract yet.
    chain = RobinhoodMainnetChain(rpc=RPC, blockscout_api_key="test-key")

    chain.register_abi(VAULT, SAMPLE_ABI)

    with patch.object(chain, "_fetch_abi_from_web", new=AsyncMock()) as fetch:
        assert await chain.load_abi(VAULT) == SAMPLE_ABI
        assert await chain.load_abi(VAULT.lower()) == SAMPLE_ABI
        fetch.assert_not_called()


def test__register_abi__evicts_cached_contract():
    chain = RobinhoodMainnetChain(rpc=RPC, blockscout_api_key="test-key")
    chain._contracts[Web3.to_checksum_address(VAULT)] = "stale"

    chain.register_abi(VAULT, SAMPLE_ABI)

    assert Web3.to_checksum_address(VAULT) not in chain._contracts
