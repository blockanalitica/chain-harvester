import json
import os
import tempfile

from chain_harvester.chain import Chain
from chain_harvester.networks.ethereum.mainnet import EthereumMainnetChain

RPC_NODES = {"ethereum": {"mainnet": "http://localhost:8545"}}


def test_chain():
    chain = Chain(rpc="http://localhost:8545")
    assert chain.rpc == "http://localhost:8545"
    assert chain.step == 10_000


def test__rpc():
    chain = EthereumMainnetChain(rpc="http://localhost:8545")
    assert chain.rpc == "http://localhost:8545"


def test__rpc_nodes():
    chain = EthereumMainnetChain(rpc_nodes=RPC_NODES)
    assert chain.rpc == RPC_NODES["ethereum"]["mainnet"]


def test__load_abi__abi():
    with tempfile.TemporaryDirectory() as temp_dir:
        contract_address = "0xExampleAddress"
        sample_abi = {"example": "abi"}
        abi_path = os.path.join(temp_dir, f"{contract_address}.json")

        with open(abi_path, "w") as f:
            json.dump(sample_abi, f)

        chain = EthereumMainnetChain(rpc_nodes=RPC_NODES, abis_path=temp_dir)

        chain.get_abi_from_source = lambda address: sample_abi
        chain.get_implementation_address = (
            lambda address: "0x0000000000000000000000000000000000000000"
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

        chain = EthereumMainnetChain(rpc_nodes=RPC_NODES, abis_path=temp_dir)

        chain.get_abi_from_source = lambda address: sample_abi

        loaded_abi = chain.load_abi(contract_address)
        assert loaded_abi == sample_abi

        assert os.path.exists(abi_path)
