from types import SimpleNamespace

from web3.exceptions import Web3RPCError

from chain_harvester_async.chain import Chain

BLOCK_RANGE_MSG = (
    "You can make eth_getLogs requests with up to a 10000 block range. "
    "Based on your parameters, this block range should work: [0x7a63, 0xa172]"
)


async def test__fetch_logs_from_rpc__shrinks_step_on_block_range_error():
    chain = Chain(chain="ethereum", network="mainnet", rpc="http://localhost:8545")

    calls = []

    async def get_logs(filters):
        calls.append((int(filters["fromBlock"], 16), int(filters["toBlock"], 16)))
        if len(calls) == 1:
            raise Web3RPCError(
                BLOCK_RANGE_MSG,
                rpc_response={"error": {"code": -32600, "message": BLOCK_RANGE_MSG}},
            )
        return []

    chain._w3 = SimpleNamespace(eth=SimpleNamespace(get_logs=get_logs))

    logs = [
        log
        async for log in chain._fetch_logs_from_rpc(
            ["0x1111111111111111111111111111111111111111"], 31331, 51331
        )
    ]

    assert logs == []
    # first call is the full range and gets rejected
    assert calls[0] == (31331, 51330)
    # retries use the step extracted from the error message (0xa172 - 0x7a63 = 9999)
    for from_block, to_block in calls[1:]:
        assert to_block - from_block < 9999
    assert calls[-1][1] == 51331
