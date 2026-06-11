from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from chain_harvester.exceptions import ArchiveHeightBehindError
from chain_harvester_async.adapters.envio import fetch_enriched_events


def make_response(next_block, archive_height, blocks=None, logs=None):
    return SimpleNamespace(
        next_block=next_block,
        archive_height=archive_height,
        data=SimpleNamespace(blocks=blocks or [], logs=logs or []),
    )


def make_chain(responses):
    chain = MagicMock()
    chain.block_store = None
    chain.hypersync_client.get = AsyncMock(side_effect=responses)
    return chain


async def test_raises_when_archive_height_behind_requested_to_block():
    chain = make_chain([make_response(next_block=971, archive_height=970)])

    events = fetch_enriched_events(chain, ["0xabc"], 950, 988)

    with pytest.raises(ArchiveHeightBehindError) as exc_info:
        await anext(events)
    assert exc_info.value.to_block == 988
    assert exc_info.value.archive_height == 970


async def test_raises_when_archive_height_falls_behind_mid_pagination():
    chain = make_chain(
        [
            make_response(next_block=960, archive_height=1000),
            make_response(next_block=970, archive_height=980),
        ]
    )

    events = fetch_enriched_events(chain, ["0xabc"], 950, 988)

    with pytest.raises(ArchiveHeightBehindError) as exc_info:
        await anext(events)
    assert exc_info.value.to_block == 988
    assert exc_info.value.archive_height == 980


async def test_yields_events_when_archive_covers_range():
    block = SimpleNamespace(number=960, hash="0x" + "11" * 32, timestamp=hex(1700000000))
    log_entry = SimpleNamespace(
        log_index=0,
        transaction_index=0,
        transaction_hash="0x" + "22" * 32,
        block_number=960,
        block_hash="0x" + "11" * 32,
        address="0xabc",
        data="0x",
        topics=["0x" + "33" * 32],
    )
    chain = make_chain(
        [make_response(next_block=989, archive_height=1000, blocks=[block], logs=[log_entry])]
    )
    chain.get_contract = AsyncMock(return_value=MagicMock())
    chain._decode_raw_log = MagicMock(return_value={"event": "Staked"})

    events = [event async for event in fetch_enriched_events(chain, ["0xabc"], 950, 988)]

    assert len(events) == 1
    assert events[0]["event"] == "Staked"
    assert events[0]["blockTimestamp"] == 1700000000
