import logging
from datetime import UTC, datetime

from hexbytes import HexBytes

from chain_harvester_async.utils.http import retry_post_json

log = logging.getLogger(__name__)


class BlockStore:
    async def get_blocks_by_numbers(self, chain_id, block_numbers):
        raise NotImplementedError

    async def save_blocks(self, chain_id, blocks):
        raise NotImplementedError


async def fetch_blocks_from_rpc(rpc, block_numbers):
    log.debug("Fetching %s blocks from RPC", len(block_numbers))

    if len(block_numbers) > 1000:
        raise ValueError("Cannot fetch more than 1000 blocks at a time from RPC")

    blocks = {}

    payload = []
    for block_number in block_numbers:
        payload.append(
            {
                "jsonrpc": "2.0",
                "id": block_number,
                "method": "eth_getBlockByNumber",
                "params": [HexBytes(block_number).to_0x_hex(), False],
            }
        )

    headers = {"content-type": "application/json"}
    response = await retry_post_json(rpc, json=payload, headers=headers)
    for resp in response:
        if "error" in resp:
            log.error(
                "Error response from RPC when fetching block: %s",
                resp["id"],
                extra={"response": resp},
            )
            continue

        info = resp["result"]
        if not info:
            log.error(
                "No result returned when fetching block: %s",
                resp["id"],
                extra={"response": resp},
            )
            continue

        block_number = int(info["number"], 16)
        if resp["id"] != block_number:
            log.error(
                "Response ID and block number don't match: %s != %s",
                resp["id"],
                block_number,
                extra={"response": resp},
            )
            continue

        timestamp = int(info["timestamp"], 16)
        blocks[block_number] = {
            "number": block_number,
            "hash": HexBytes(info["hash"]),
            "timestamp": timestamp,
            "datetime": datetime.fromtimestamp(timestamp, tz=UTC),
        }

    missing_blocks = block_numbers - set(blocks.keys())
    if missing_blocks:
        log.warning("Couldn't fetch blocks %s from RPC", missing_blocks)

    return blocks


async def fetch_block_info(chain, block_numbers):
    block_numbers = set(block_numbers)

    if chain.block_store and isinstance(chain.block_store, BlockStore):
        store = chain.block_store
    else:
        store = None
        log.warning(
            "Block store is not set or not of correct type, "
            "always fetching fresh blocks info from RPC"
        )

    if store:
        # TODO: validate that we get blocks in correct format
        blocks = await store.get_blocks_by_numbers(chain.chain_id, block_numbers)
        missing_blocks = block_numbers - set(blocks.keys())
    else:
        blocks = {}
        missing_blocks = block_numbers

    if missing_blocks:
        rpc_blocks = await fetch_blocks_from_rpc(chain.rpc, missing_blocks)
        blocks.update(rpc_blocks)
        if store:
            await store.save_blocks(chain.chain_id, rpc_blocks.values())

    return blocks
