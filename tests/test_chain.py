import json
import os
import tempfile

from chain_harvester.chain import Chain


def test_chain():
    chain = Chain(rpc="http://localhost:8545")
    assert chain.rpc == "http://localhost:8545"
    assert chain.step == 10_000


def test_load_abi__abi():
    with tempfile.TemporaryDirectory() as temp_dir:
        contract_address = "0xExampleAddress"
        sample_abi = {"example": "abi"}
        abi_path = os.path.join(temp_dir, f"{contract_address}.json")

        with open(abi_path, "w") as f:
            json.dump(sample_abi, f)

        chain = Chain(abis_path=temp_dir)

        chain.get_abi_from_etherscan = lambda address: sample_abi

        loaded_abi = chain.load_abi(contract_address)
        assert loaded_abi == sample_abi

        assert os.path.exists(abi_path)


def test_load_abi__contract():
    with tempfile.TemporaryDirectory() as temp_dir:
        contract_address = "0x6b175474e89094c44da98b954eedeac495271d0f"
        sample_abi = {"example": "abi"}
        abi_path = os.path.join(temp_dir, f"{contract_address}.json")

        with open(abi_path, "w") as f:
            json.dump(sample_abi, f)

        chain = Chain(abis_path=temp_dir)

        chain.get_abi_from_etherscan = lambda address: sample_abi

        loaded_abi = chain.load_abi(contract_address)
        assert loaded_abi == sample_abi

        assert os.path.exists(abi_path)
