import pytest

from chain_harvester_async.utils.s3 import fetch_abi_from_s3, save_abi_to_s3
from integration_tests.constants import DEMO_ABI


async def test_fetch_abi_from_s3():
    config = {
        "bucket_name": "abis-787309967787",
        "dir": "test",
        "chain": "ethereum",
        "network": "mainnet",
        "region": "eu-west-1",
    }
    contact_address = "0xA9C3D3a366466fa809d1ae982fb2c46e5fc41101"

    abi = await fetch_abi_from_s3(config, contact_address)
    assert abi == DEMO_ABI


@pytest.mark.skip(reason="Only for manual testing")
async def test_save_abi_to_s3():
    config = {
        "bucket_name": "abis-787309967787",
        "dir": "test",
        "chain": "ethereum",
        "network": "mainnet",
        "region": "eu-west-1",
    }
    contact_address = "0xA9C3D3a366466fa809d1ae982fb2c46e5fc41101"

    await save_abi_to_s3(config, contact_address, DEMO_ABI)
