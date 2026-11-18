from datetime import UTC, date, datetime
from unittest.mock import AsyncMock, patch

import pytest

from chain_harvester.constants import MULTICALL3_ADDRESSES
from chain_harvester.exceptions import ChainException
from chain_harvester_async.helpers import get_chain
from chain_harvester_async.networks import ElysiumMainnetChain

RPC = "http://localhost:1"
EXPLORER_API = "https://elysium.kinetiq.xyz/api"

GENESIS = int(datetime(2026, 9, 25, tzinfo=UTC).timestamp())
HEAD = 200_000
CLOSING_BLOCK = 86_399


def fake_rpc_blocks(chain, monkeypatch):
    async def get_block_info(block_number):
        if not 0 <= block_number <= HEAD:
            raise ValueError(f"block {block_number} does not exist")
        timestamp = GENESIS + block_number
        return {
            "number": block_number,
            "timestamp": timestamp,
            "datetime": datetime.fromtimestamp(timestamp, tz=UTC),
        }

    async def get_latest_block_number(offset=None):
        return HEAD

    monkeypatch.setattr(chain, "get_block_info", get_block_info)
    monkeypatch.setattr(chain, "get_latest_block_number", get_latest_block_number)


def test_elysium_chain_config():
    chain = ElysiumMainnetChain(rpc=RPC)

    assert chain.chain_id == 99901
    assert chain.get_multicall_address() == "0xcA11bde05977b3631167028862bE2a173976CA11"
    assert MULTICALL3_ADDRESSES[99901] == chain.get_multicall_address()
    assert chain.kinetiq_url == EXPLORER_API
    assert isinstance(get_chain("elysium", rpc=RPC), ElysiumMainnetChain)


def test_elysium_never_uses_hypersync():
    chain = ElysiumMainnetChain(rpc=RPC, use_hypersync=True, hypersync_api_key="key")

    assert chain.use_hypersync is False
    assert not hasattr(chain, "hypersync_client")


async def test_get_abi_from_source():
    chain = ElysiumMainnetChain(rpc=RPC)
    with patch(
        "chain_harvester_async.mixins.kinetiq.retry_get_json",
        AsyncMock(return_value={"message": "OK", "result": '[{"type": "event"}]', "status": "1"}),
    ) as m:
        assert await chain.get_abi_from_source("0xABC") == [{"type": "event"}]
    m.assert_awaited_once_with(
        f"{EXPLORER_API}?module=contract&action=getabi&address=0xABC", timeout=30
    )


async def test_get_abi_from_source_raises_for_unverified_contract():
    chain = ElysiumMainnetChain(rpc=RPC)
    with (
        patch(
            "chain_harvester_async.mixins.kinetiq.retry_get_json",
            AsyncMock(
                return_value={
                    "message": "Contract source code not verified",
                    "result": None,
                    "status": "0",
                }
            ),
        ),
        pytest.raises(ChainException),
    ):
        await chain.get_abi_from_source("0xABC")


async def test_get_closest_block_before_timestamp():
    chain = ElysiumMainnetChain(rpc=RPC)
    with patch(
        "chain_harvester_async.mixins.kinetiq.retry_get_json",
        AsyncMock(return_value={"message": "OK", "result": {"blockNumber": "7290248"}}),
    ) as m:
        assert await chain.get_closest_block_before_timestamp(1794876268) == 7290248
    m.assert_awaited_once_with(
        f"{EXPLORER_API}?module=block&action=getblocknobytime&timestamp=1794876268&closest=before",
        timeout=30,
    )


async def test_closing_block_from_explorer(monkeypatch):
    chain = ElysiumMainnetChain(rpc=RPC)
    fake_rpc_blocks(chain, monkeypatch)
    with patch(
        "chain_harvester_async.mixins.kinetiq.retry_get_json",
        AsyncMock(return_value={"message": "OK", "result": {"blockNumber": str(CLOSING_BLOCK)}}),
    ):
        block = await chain.get_closing_block_info(date(2026, 9, 25))

    assert block["number"] == CLOSING_BLOCK


@pytest.mark.parametrize(
    "explorer",
    [
        AsyncMock(side_effect=TimeoutError),
        AsyncMock(return_value="<html>Vercel Security Checkpoint</html>"),
    ],
)
async def test_closing_block_falls_back_to_rpc_search_without_defillama(monkeypatch, explorer):
    chain = ElysiumMainnetChain(rpc=RPC)
    fake_rpc_blocks(chain, monkeypatch)
    defillama = AsyncMock()
    with (
        patch("chain_harvester_async.mixins.kinetiq.retry_get_json", explorer),
        patch(
            "chain_harvester_async.chain.defillama.get_closest_block_before_timestamp", defillama
        ),
    ):
        block = await chain.get_closing_block_info(date(2026, 9, 25))

    assert block["number"] == CLOSING_BLOCK
    defillama.assert_not_awaited()
