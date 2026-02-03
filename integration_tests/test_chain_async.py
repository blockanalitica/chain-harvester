import os

import aiofiles
import aiofiles.os
import aiofiles.ospath as ospath
from web3 import Web3

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


async def test_get_events_for_contract(chain):
    events = chain.get_events_for_contract(USDS_CONTRACT, 23865574, 23865583)
    events = [event async for event in events]
    assert len(events) == 19


async def test_get_events_for_contracts(chain):
    events = chain.get_events_for_contracts([USDS_CONTRACT], 23865574, 23865583)
    events = [event async for event in events]
    assert len(events) == 19


async def test_get_events_for_contract_topics(chain):
    events = chain.get_events_for_contract_topics(
        USDS_CONTRACT,
        ["0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"],
        23865574,
        23865583,
    )
    events = [event async for event in events]
    assert len(events) == 16


async def test_get_events_for_contracts_topics(chain):
    events = chain.get_events_for_contracts_topics(
        [USDS_CONTRACT],
        ["0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"],
        23865574,
        23865583,
    )
    events = [event async for event in events]
    assert len(events) == 16


async def test_get_events_for_topics(chain):
    events = chain.get_events_for_topics(
        ["0xe1fffcc4923d04b559f4d29a8bfc6cda04eb5b0d3c460751c2402c5c5cc9109c"],
        23865576,
        23865577,
    )
    events = [event async for event in events]
    assert len(events) == 21


async def test_get_latest_event_before_block(chain):
    event = await chain.get_latest_event_before_block(
        USDS_CONTRACT,
        ["0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"],
        23865575,
    )
    assert (
        event["transactionHash"].to_0x_hex()
        == "0x69458d70f63bc224f30bf46448d38592e4a90cf276216883b0baa4608ecfdec2"
    )


async def test_abi_to_event_topics(chain):
    topics = await chain.abi_to_event_topics(USDS_CONTRACT)
    assert list(topics.keys()) == [
        "0x8c5be1e5ebec7d5bd14f71427d1e84f3dd0314c0f7b2291e5b200ac8c7c3b925",
        "0x184450df2e323acec0ed3b5c7531b81f9b4cdef7914dfd4c0a4317416bb5251b",
        "0xc7f505b2f371ae2175ee4913f4499e1f2633a7b5936321eed1cdaeb6115181d2",
        "0xdd0e34038ac38b2a1ce960229778ac48a8719bc900b6c4f8d0475c6e8b385a60",
        "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef",
        "0xbc7cd75a20ee27fd9adebab32041f755214dbc6bffa90cc0225b39da2e5c2d3b",
    ]


async def test_get_events_topics(chain):
    topics = await chain.get_events_topics(USDS_CONTRACT)
    assert topics == [
        "0x8c5be1e5ebec7d5bd14f71427d1e84f3dd0314c0f7b2291e5b200ac8c7c3b925",
        "0x184450df2e323acec0ed3b5c7531b81f9b4cdef7914dfd4c0a4317416bb5251b",
        "0xc7f505b2f371ae2175ee4913f4499e1f2633a7b5936321eed1cdaeb6115181d2",
        "0xdd0e34038ac38b2a1ce960229778ac48a8719bc900b6c4f8d0475c6e8b385a60",
        "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef",
        "0xbc7cd75a20ee27fd9adebab32041f755214dbc6bffa90cc0225b39da2e5c2d3b",
    ]


async def test_batch_eth_calls(chain):
    calls = [
        (
            "0xFc21d6d146E6086B8359705C8b28512a983db0cb",
            "getReserveData",
            23865575,
            [Web3.to_checksum_address(USDS_CONTRACT)],
        )
    ]
    response = await chain.batch_eth_calls(calls)
    assert response[0]["totalAToken"] == 471848186538525756021645047


async def test_get_token_info(chain):
    token = await chain.get_token_info(USDS_CONTRACT)
    assert token["symbol"] == "USDS"
    assert token["name"] == "USDS Stablecoin"
    assert token["decimals"] == 18


async def test_get_token_info_32(chain):
    # MKR is bytes32 encoded
    token = await chain.get_token_info("0x9f8f72aa9304c8b593d555f12ef6589cc3a579a2")
    assert token["symbol"] == "MKR"
    assert token["name"] == "Maker"
    assert token["decimals"] == 18


async def test_get_timestamp_for_block(chain):
    ts = await chain.get_timestamp_for_block(23865575)
    assert ts == 1763949167


async def test_get_block_for_timestamp(chain):
    block = await chain.get_block_for_timestamp(1763949167)
    assert block == 23865575


async def test_get_block_for_timestamp_fallback(chain):
    chain.chain = "1337"
    block = await chain.get_block_for_timestamp(1763949167)
    assert block == 23865575


async def test_get_erc4626_info(chain):
    info = await chain.get_erc4626_info("0x9d39a5de30e57443bff2a8307a4256c8797a3497", 23865575)

    assert info == {
        "name": "Staked USDe",
        "symbol": "sUSDe",
        "asset": "0x4c9edd5852cd905f086c759e8383e09bff1e68b3",
        "decimals": 18,
        "total_assets": 4342186856971269938740586743,
        "total_supply": 3593513370578111124158301804,
        "convert_to_assets": 1208340253447481954534744261468,
    }
