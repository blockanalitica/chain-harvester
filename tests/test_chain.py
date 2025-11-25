import json
import os
import tempfile
from unittest.mock import patch

import pytest

from chain_harvester.chain import Chain

USDS_CONTRACT = "0xdc035d45d973e3ec169d2276ddab16f1e407384f"


class DummyChain(Chain):
    pass


@pytest.fixture
async def chain():
    return DummyChain(
        chain="ethereum",
        network="mainnet",
        chain_id=1,
        rpc="http://localhost:8545",
    )


def test_chain(chain):
    assert chain.rpc == "http://localhost:8545"
    assert chain.step == 10_000
    assert chain.chain_id == 1
    assert chain.chain == "ethereum"
    assert chain.network == "mainnet"


async def test_get_abi_from_source(chain):
    with pytest.raises(NotImplementedError):
        await chain.get_abi_from_source(USDS_CONTRACT)


def test_get_multicall_address(chain):
    assert chain.get_multicall_address() == "0xcA11bde05977b3631167028862bE2a173976CA11"


async def test__load_abi__abi():
    with tempfile.TemporaryDirectory() as temp_dir:
        contract_address = "0xExampleAddress"
        sample_abi = {"example": "abi"}
        abi_path = os.path.join(temp_dir, f"{contract_address}.json")

        with open(abi_path, "w") as f:
            json.dump(sample_abi, f)

        chain = Chain(
            chain="ethereum",
            network="mainnet",
            chain_id=1,
            rpc="http://localhost:8545",
            abis_path=temp_dir,
        )

        with patch.object(chain, "_fetch_abi_from_web", return_value=sample_abi):
            loaded_abi = await chain.load_abi(contract_address)
            assert loaded_abi == sample_abi

        assert os.path.exists(abi_path)


async def test__load_abi__contract():
    with tempfile.TemporaryDirectory() as temp_dir:
        contract_address = "0x6b175474e89094c44da98b954eedeac495271d0f"
        sample_abi = {"example": "abi"}
        abi_path = os.path.join(temp_dir, f"{contract_address}.json")

        with open(abi_path, "w") as f:
            json.dump(sample_abi, f)

        chain = Chain(
            chain="ethereum",
            network="mainnet",
            chain_id=1,
            rpc="http://localhost:8545",
            abis_path=temp_dir,
        )

        with patch.object(chain, "_fetch_abi_from_web", return_value=sample_abi):
            loaded_abi = await chain.load_abi(contract_address)
            assert loaded_abi == sample_abi

        assert os.path.exists(abi_path)


def test_chainlink_price_feed_for_asset_symbol(chain):
    feed = chain.chainlink_price_feed_for_asset_symbol("DAI")
    assert feed == "0xAed0c38402a5d19df6E4c03F4E2DceD6e29c1ee9"


def test_chainlink_price_feed_for_asset_symbol_mapping(chain):
    feed = chain.chainlink_price_feed_for_asset_symbol("WETH")
    assert feed == "0x5f4eC3Df9cbd43714FE2740f5E3616155c5b8419"
