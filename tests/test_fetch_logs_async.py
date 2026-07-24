from unittest.mock import AsyncMock

from chain_harvester_async.chain import Chain

RPC_NODES = {
    "ethereum": {
        "mainnet": "http://localhost:8545",
    },
}


def make_chain():
    return Chain(
        chain="ethereum",
        network="mainnet",
        rpc="http://localhost:8545",
        step=10_000,
    )


async def collect_logs(chain, from_block, to_block):
    return [log async for log in chain._fetch_logs_from_rpc([], from_block, to_block)]


async def test_fetch_logs_single_block_range_terminates(monkeypatch):
    """from_block == to_block is a 1-block range: one request, no infinite loop."""
    chain = make_chain()
    get_logs = AsyncMock(return_value=[])
    eth = type("Eth", (), {"get_logs": get_logs})()
    monkeypatch.setattr(chain, "_w3", type("W3", (), {"eth": eth})())

    logs = await collect_logs(chain, 100, 100)

    assert logs == []
    assert get_logs.await_count == 1
    filters = get_logs.await_args.args[0]
    assert filters["fromBlock"] == hex(100)
    assert filters["toBlock"] == hex(100)


async def test_fetch_logs_chunks_cover_full_inclusive_range(monkeypatch):
    """Windows advance past the fetched end_block and cover [from, to] exactly once."""
    chain = make_chain()
    chain.step = 10
    seen = []

    async def fake_get_logs(filters):
        seen.append((int(filters["fromBlock"], 16), int(filters["toBlock"], 16)))
        return []

    eth = type("Eth", (), {"get_logs": staticmethod(fake_get_logs)})()
    monkeypatch.setattr(chain, "_w3", type("W3", (), {"eth": eth})())

    await collect_logs(chain, 0, 24)

    assert seen == [(0, 9), (10, 19), (20, 24)]
