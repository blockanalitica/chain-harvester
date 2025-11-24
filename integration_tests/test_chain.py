import os

import aiofiles
import aiofiles.os
import aiofiles.ospath as ospath

from integration_tests.constants import DEMO_ABI


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
