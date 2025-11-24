import os

import aiofiles
import aiofiles.os
import aiofiles.ospath as ospath

from integration_tests.constants import DEMO_ABI, USDS_CONTRACT


async def test_get_latest_block(chain):
    latest = await chain.get_latest_block()
    assert latest > 0
    assert isinstance(latest, int)


async def test_get_latest_block_offset(chain):
    latest = await chain.get_latest_block(offset=0)
    with_offset = await chain.get_latest_block(offset=100)
    # Test that offset is lower than the latest but not for full amount as there's delay
    # between the calls so it's not necessary that chain returns the same block number
    assert with_offset < latest - 90


async def test_get_block_info(chain):
    block = await chain.get_block_info(23696969)
    assert len(block.transactions) == 171
    assert block.number == 23696969
    assert (
        block.hash.to_0x_hex()
        == "0x7452a43b26b41f70df0c59e53f5bf447df8e9f5587d312b90e0aeafc9655b7e4"
    )


async def test_load_abi_from_web(chain):
    address = "0xA9c3D3a366466Fa809d1Ae982Fb2c46E5fC41101"
    # Make sure to delete the file first
    file_path = os.path.join(chain.abis_path, f"{address.lower()}.json")
    if await ospath.exists(file_path):
        await aiofiles.os.remove(file_path)

    abi = await chain.load_abi(address)
    assert abi == DEMO_ABI


async def test_load_abi_from_s3(chain):
    address = "0xA9c3D3a366466Fa809d1Ae982Fb2c46E5fC41101"
    chain.s3_config = {
        "bucket_name": "abis-787309967787",
        "dir": "test",
        "chain": "ethereum",
        "network": "mainnet",
        "region": "eu-west-1",
    }
    # Make sure to delete the file first
    file_path = os.path.join(chain.abis_path, f"{address.lower()}.json")
    if await ospath.exists(file_path):
        await aiofiles.os.remove(file_path)

    abi = await chain.load_abi(address)
    assert abi == DEMO_ABI


async def test_get_contract(chain):
    contract = await chain.get_contract(USDS_CONTRACT)
    assert contract.address.lower() == USDS_CONTRACT


async def test_call_contract_function(chain):
    symbol = await chain.call_contract_function(USDS_CONTRACT, "symbol")
    assert symbol == "USDS"


async def test_get_storage_at(chain):
    slot = "0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc"
    content = await chain.get_storage_at(USDS_CONTRACT, int(slot, 16), 23865574)
    assert content == "0000000000000000000000001923dfee706a8e78157416c29cbccfde7cdf4102"


async def test_get_code(chain):
    code = await chain.get_code(USDS_CONTRACT)
    assert code == (
        "6080604052600a600c565b005b60186014601a565b6051565b565b6000604c7f360894a13ba1a"
        "3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc546001600160a01b031690565b"
        "905090565b3660008037600080366000845af43d6000803e808015606f573d6000f35b3d6000f"
        "dfea2646970667358221220fb4fe6c40bd8fec38fd16b0ec231b1d502f3cbafe4e1c2483e3b4a"
        "61e9b3a17264736f6c63430008150033"
    )
