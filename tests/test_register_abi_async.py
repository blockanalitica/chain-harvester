import json
from unittest.mock import AsyncMock, patch

from web3 import Web3

from chain_harvester_async.networks import RobinhoodMainnetChain

RPC = "http://localhost:1"
VAULT = "0x19D55F7Fe2d3962796F5825cbdaE2dD493Be0986"
SAMPLE_ABI = [{"type": "event", "name": "Deposit", "inputs": [], "anonymous": False}]


async def test__register_abi__skips_lookup(tmp_path):
    # A registered ABI must be served from the cache without touching local
    # storage, S3, or the explorer — the whole point is that the explorer may
    # not have matched the contract yet.
    chain = RobinhoodMainnetChain(rpc=RPC, blockscout_api_key="test-key", abis_path=str(tmp_path))

    await chain.register_abi(VAULT, SAMPLE_ABI)

    with patch.object(chain, "_fetch_abi_from_web", new=AsyncMock()) as fetch:
        assert await chain.load_abi(VAULT) == SAMPLE_ABI
        assert await chain.load_abi(VAULT.lower()) == SAMPLE_ABI
        fetch.assert_not_called()


async def test__register_abi__persists_to_local_file(tmp_path):
    # A fresh chain (next cron run) must find the registered ABI on disk instead
    # of falling through to the explorer.
    chain = RobinhoodMainnetChain(rpc=RPC, blockscout_api_key="test-key", abis_path=str(tmp_path))

    await chain.register_abi(VAULT, SAMPLE_ABI)

    assert json.loads((tmp_path / f"{VAULT.lower()}.json").read_text()) == SAMPLE_ABI
    fresh = RobinhoodMainnetChain(rpc=RPC, blockscout_api_key="test-key", abis_path=str(tmp_path))
    with patch.object(fresh, "_fetch_abi_from_web", new=AsyncMock()) as fetch:
        assert await fresh.load_abi(VAULT) == SAMPLE_ABI
        fetch.assert_not_called()


async def test__register_abi__persists_to_s3(tmp_path):
    chain = RobinhoodMainnetChain(
        rpc=RPC,
        blockscout_api_key="test-key",
        abis_path=str(tmp_path),
        s3={"bucket_name": "bucket", "dir": "app"},
    )

    with patch("chain_harvester_async.chain.save_abi_to_s3", new=AsyncMock()) as save:
        await chain.register_abi(VAULT, SAMPLE_ABI)

    save.assert_awaited_once_with(chain.s3_config, VAULT.lower(), SAMPLE_ABI)


async def test__register_abi__evicts_cached_contract(tmp_path):
    chain = RobinhoodMainnetChain(rpc=RPC, blockscout_api_key="test-key", abis_path=str(tmp_path))
    chain._contracts[Web3.to_checksum_address(VAULT)] = "stale"

    await chain.register_abi(VAULT, SAMPLE_ABI)

    assert Web3.to_checksum_address(VAULT) not in chain._contracts
