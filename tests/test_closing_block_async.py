from datetime import UTC, date, datetime

import pytest

from chain_harvester.exceptions import ChainException
from chain_harvester_async.blocks import BlockStore
from chain_harvester_async.networks import EthereumMainnetChain

RPC_NODES = {"ethereum": {"mainnet": "http://localhost:8545"}}

# Block n is mined at GENESIS + 2n seconds; the chain head is HEAD.
GENESIS = int(datetime(2026, 9, 25, tzinfo=UTC).timestamp())
HEAD = 50_000
# 2026-09-25 23:59:59: block 43_199 (23:59:58) closes the day, 43_200 opens the next.
END_OF_DAY = GENESIS + 86_399
CLOSING_BLOCK = 43_199


class FakeBlockStore(BlockStore):
    def __init__(self, closing_block=None):
        self.closing_block = closing_block
        self.saved = []

    async def get_block_by_number(self, chain_id, block_number):
        return None

    async def save_blocks(self, chain_id, blocks):
        pass

    async def get_closing_block(self, chain_id, for_date):
        return self.closing_block

    async def save_closing_block(self, chain_id, block):
        self.saved.append(block["number"])


@pytest.fixture
def chain(monkeypatch):
    chain = EthereumMainnetChain(
        rpc_nodes=RPC_NODES, etherscan_api_key="1234", block_store=FakeBlockStore()
    )
    chain.lookups = []

    async def get_block_info(block_number):
        if not 0 <= block_number <= HEAD:
            raise ValueError(f"block {block_number} does not exist")
        chain.lookups.append(block_number)
        timestamp = GENESIS + 2 * block_number
        return {
            "number": block_number,
            "timestamp": timestamp,
            "datetime": datetime.fromtimestamp(timestamp, tz=UTC),
        }

    async def get_latest_block_number(offset=None):
        return HEAD

    monkeypatch.setattr(chain, "get_block_info", get_block_info)
    monkeypatch.setattr(chain, "get_latest_block_number", get_latest_block_number)
    return chain


async def test_find_closing_block_accepts_the_right_answer_with_one_extra_lookup(chain):
    block = await chain.find_closing_block(END_OF_DAY, CLOSING_BLOCK)

    assert block["number"] == CLOSING_BLOCK
    assert chain.lookups == [CLOSING_BLOCK, CLOSING_BLOCK + 1, CLOSING_BLOCK]


@pytest.mark.parametrize(
    "looked_up",
    [
        CLOSING_BLOCK - 1,
        CLOSING_BLOCK - 172,  # an explorer index lagging ~6 minutes
        0,
        CLOSING_BLOCK + 1,
        CLOSING_BLOCK + 500,
        HEAD,
    ],
)
async def test_find_closing_block_corrects_a_wrong_answer(chain, looked_up):
    block = await chain.find_closing_block(END_OF_DAY, looked_up)

    assert block["number"] == CLOSING_BLOCK


async def test_find_closing_block_refuses_a_day_that_is_not_over(chain):
    with pytest.raises(ChainException, match="not over"):
        await chain.find_closing_block(GENESIS + 2 * HEAD + 10, HEAD - 3)


async def test_find_closing_block_refuses_a_time_before_the_first_block(chain):
    with pytest.raises(ChainException, match="at or before"):
        await chain.find_closing_block(GENESIS - 1, 10)


async def test_get_closing_block_info_saves_the_corrected_block(chain, monkeypatch):
    async def lagging_lookup(timestamp):
        return CLOSING_BLOCK - 172

    monkeypatch.setattr(chain, "get_closest_block_before_timestamp", lagging_lookup)

    block = await chain.get_closing_block_info(date(2026, 9, 25))

    assert block["number"] == CLOSING_BLOCK
    assert chain.block_store.saved == [CLOSING_BLOCK]
