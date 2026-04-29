import logging
from datetime import UTC, datetime

from hexbytes import HexBytes
from hypersync import (
    BlockField,
    ClientConfig,
    FieldSelection,
    HypersyncClient,
    JoinMode,
    LogField,
    LogSelection,
    Query,
)

from chain_harvester.decoders import MissingABIEventDecoderError
from chain_harvester_async.blocks import BlockStore

log = logging.getLogger(__name__)


async def _decode_envio_log(chain, log_entry, mixed, anonymous):
    contract = await chain.get_contract(log_entry.address.lower())
    log_data = {
        "logIndex": log_entry.log_index,
        "transactionIndex": log_entry.transaction_index,
        "transactionHash": HexBytes(log_entry.transaction_hash),
        "blockNumber": log_entry.block_number,
        "blockHash": HexBytes(log_entry.block_hash),
        "address": log_entry.address,
        "data": HexBytes(log_entry.data),
        "topics": [HexBytes(t) for t in log_entry.topics if t],
    }
    try:
        data = chain._decode_raw_log(contract, log_data, mixed, anonymous)
    except MissingABIEventDecoderError:
        log.warning(
            "Contract ABI (%s) is missing an event definition. Fetching a new ABI on block %s",
            log_data["address"].lower(),
            log_data["blockNumber"],
        )
        contract = await chain.get_contract(
            log_data["address"].lower(),
            refetch_on_block=log_data["blockNumber"],
        )
        data = chain._decode_raw_log(contract, log_data, mixed, anonymous)

    return data


async def fetch_enriched_events(
    chain,
    contract_addresses,
    from_block,
    to_block,
    topics=None,
    anonymous=False,
    mixed=False,
):
    hypersync_url = f"https://{chain.chain_id}.hypersync.xyz"

    client = HypersyncClient(ClientConfig(url=hypersync_url, bearer_token=chain.hypersync_api_key))

    call_count = 0
    while from_block < to_block:
        query = Query(
            from_block=from_block,
            to_block=to_block,
            logs=[
                LogSelection(
                    address=contract_addresses,
                    topics=topics,
                )
            ],
            join_mode=JoinMode.DEFAULT,
            field_selection=FieldSelection(
                block=[
                    BlockField.NUMBER,
                    BlockField.TIMESTAMP,
                    BlockField.HASH,
                    BlockField.PARENT_HASH,
                ],
                log=[
                    LogField.LOG_INDEX,
                    LogField.TRANSACTION_INDEX,
                    LogField.TRANSACTION_HASH,
                    LogField.BLOCK_NUMBER,
                    LogField.BLOCK_HASH,
                    LogField.ADDRESS,
                    LogField.DATA,
                    LogField.TOPIC0,
                    LogField.TOPIC1,
                    LogField.TOPIC2,
                    LogField.TOPIC3,
                ],
            ),
        )
        log.debug("Fetching events for contracts topics from block %s to %s", from_block, to_block)
        res = await client.get(query)
        call_count += 1

        from_block = res.next_block

        # Set to_block to res.archive_height on first request if it's bigger than
        # res.archive_height to prevent infinte loop (especially on fast chains)
        if call_count == 1 and to_block > res.archive_height:
            to_block = res.archive_height

        blocks = {}
        for block in res.data.blocks:
            blocks[block.number] = {
                "number": block.number,
                "hash": HexBytes(block.hash),
                "timestamp": int(block.timestamp, 16),
                "datetime": datetime.fromtimestamp(int(block.timestamp, 16), tz=UTC),
            }

        if chain.block_store and isinstance(chain.block_store, BlockStore):
            await chain.block_store.save_blocks(chain.chain_id, blocks.values())
        else:
            log.warning(
                "Block store is not set or not of correct type, "
                "not saving blocks fetched via HyperSync"
            )

        for log_entry in res.data.logs:
            event = await _decode_envio_log(chain, log_entry, mixed, anonymous)
            block = blocks[log_entry.block_number]
            event["blockTimestamp"] = block["timestamp"]
            event["blockDateTime"] = block["datetime"]
            yield event
