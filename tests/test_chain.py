import json
import os
import tempfile
from unittest.mock import patch


import pytest
import boto3
from moto import mock_aws

from chain_harvester.chain import Chain
from chain_harvester.networks.ethereum.mainnet import EthereumMainnetChain

RPC_NODES = {"ethereum": {"mainnet": "http://localhost:8545"}}


def test_chain():
    chain = Chain(chain="ethereum", network="mainnet", rpc="http://localhost:8545")
    assert chain.rpc == "http://localhost:8545"
    assert chain.step == 10_000


def test__rpc():
    chain = EthereumMainnetChain(rpc="http://localhost:8545", etherscan_api_key="1234")
    assert chain.rpc == "http://localhost:8545"


def test__rpc_nodes():
    chain = EthereumMainnetChain(rpc_nodes=RPC_NODES, etherscan_api_key="1234")
    assert chain.rpc == RPC_NODES["ethereum"]["mainnet"]


def test__load_abi__abi():
    with tempfile.TemporaryDirectory() as temp_dir:
        contract_address = "0xExampleAddress"
        sample_abi = {"example": "abi"}
        abi_path = os.path.join(temp_dir, f"{contract_address}.json")

        with open(abi_path, "w") as f:
            json.dump(sample_abi, f)

        chain = EthereumMainnetChain(
            rpc_nodes=RPC_NODES, abis_path=temp_dir, etherscan_api_key="1234"
        )

        with patch.object(chain, "_fetch_abi_from_chain", return_value=sample_abi):
            loaded_abi = chain.load_abi(contract_address)
            assert loaded_abi == sample_abi

        assert os.path.exists(abi_path)


def test__load_abi__contract():
    with tempfile.TemporaryDirectory() as temp_dir:
        contract_address = "0x6b175474e89094c44da98b954eedeac495271d0f"
        sample_abi = {"example": "abi"}
        abi_path = os.path.join(temp_dir, f"{contract_address}.json")

        with open(abi_path, "w") as f:
            json.dump(sample_abi, f)

        chain = EthereumMainnetChain(
            rpc_nodes=RPC_NODES, abis_path=temp_dir, etherscan_api_key="1234"
        )

        with patch.object(chain, "_fetch_abi_from_chain", return_value=sample_abi):
            loaded_abi = chain.load_abi(contract_address)
            assert loaded_abi == sample_abi

        assert os.path.exists(abi_path)


def test__to_hex_topic():
    chain = EthereumMainnetChain(rpc_nodes=RPC_NODES, etherscan_api_key="1234")
    assert (
        chain.to_hex_topic("File(bytes32,bytes32,uint256)")
        == "0x851aa1caf4888170ad8875449d18f0f512fd6deb2a6571ea1a41fb9f95acbcd1"
    )


def test__multicall_address():
    chain = EthereumMainnetChain(rpc_nodes=RPC_NODES, etherscan_api_key="1234")
    assert chain.get_multicall_address() == "0xcA11bde05977b3631167028862bE2a173976CA11"


def test__chainlink_price_feed_for_asset_symbol():
    chain = EthereumMainnetChain(rpc_nodes=RPC_NODES, etherscan_api_key="1234")
    feed = chain.chainlink_price_feed_for_asset_symbol("DAI")
    assert feed == "0xAed0c38402a5d19df6E4c03F4E2DceD6e29c1ee9"


def test__chainlink_price_feed_for_asset_symbol_mapping():
    chain = EthereumMainnetChain(rpc_nodes=RPC_NODES, etherscan_api_key="1234")
    feed = chain.chainlink_price_feed_for_asset_symbol("WETH")
    assert feed == "0x5f4eC3Df9cbd43714FE2740f5E3616155c5b8419"


@pytest.fixture
def chain_with_s3(tmp_path):
    with mock_aws():
        # Set up fake S3
        s3 = boto3.client("s3", region_name="eu-west-1")
        bucket = "test-bucket"
        s3.create_bucket(
            Bucket=bucket, CreateBucketConfiguration={"LocationConstraint": "eu-west-1"}
        )

        # Build chain with fake S3
        chain = Chain(
            chain="ethereum",
            network="mainnet",
            rpc="http://fake-rpc",
            rpc_nodes={"ethereum": {"mainnet": "http://fake-rpc"}},
            abis_path=str(tmp_path),
            chain_id=1,
            s3={
                "bucket_name": bucket,
                "dir": "abis",
                "region": "eu-west-1",
            },
        )
        chain.s3 = s3

        yield chain, s3, bucket


def test_upload_and_fetch_abi(chain_with_s3):
    chain, s3, bucket = chain_with_s3
    fake_abi = [{"type": "function", "name": "transfer"}]
    address = "0x1234567890abcdef1234567890abcdef12345678"

    # load abi and mock return_value for fetching abi from chainb
    with patch.object(chain, "_fetch_abi_from_chain", return_value=fake_abi):
        chain.load_abi(address)

    # Check object really exists in fake S3
    key = f"abis/ethereum/mainnet/{address}.json"
    obj = s3.get_object(Bucket=bucket, Key=key)
    stored = json.loads(obj["Body"].read())
    assert stored == fake_abi

    assert chain._abis[address] == fake_abi

    # Fetch again and make sure we only fetch from s3 and that _fetch_abi_from_chain is not called
    chain._abis.clear()  # clear cached abis
    with patch.object(chain, "_fetch_abi_from_chain") as mock_fetch:
        chain.load_abi(address)
        assert not mock_fetch.called
    assert chain._abis[address] == fake_abi
