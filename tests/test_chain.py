import json
import os
import tempfile

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

        chain.get_abi_from_source = lambda address: sample_abi
        chain.get_implementation_address = (
            lambda address, x: "0x0000000000000000000000000000000000000000"
        )

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

        chain.get_abi_from_source = lambda address: sample_abi
        chain.get_implementation_address = (
            lambda address, x: "0x0000000000000000000000000000000000000000"
        )

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
