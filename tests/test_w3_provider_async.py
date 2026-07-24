import json
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from aiohttp import ClientResponseError

from chain_harvester_async.w3_provider import CustomHTTPSessionManager


def _response(status, body, reason="Error"):
    return SimpleNamespace(
        status=status,
        reason=reason,
        headers={},
        request_info=None,
        history=(),
        read=AsyncMock(return_value=body),
    )


async def _post(response):
    manager = CustomHTTPSessionManager()
    manager.async_get_response_from_post_request = AsyncMock(return_value=response)
    return await manager.async_make_post_request("http://localhost:8545", b"{}")


async def test_ok_json_body_passes_through():
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "result": "0x1"}).encode()
    assert await _post(_response(200, body)) == body


async def test_error_status_with_json_body_passes_through():
    # Some RPCs return the JSON-RPC error payload with a non-200 status; web3 must
    # receive it so the caller sees the RPC's own error message.
    body = json.dumps(
        {"jsonrpc": "2.0", "id": 1, "error": {"code": -32005, "message": "rate limited"}}
    ).encode()
    assert await _post(_response(429, body)) == body


async def test_error_status_with_empty_body_raises():
    # A bare 429 with an empty body must raise a retryable ClientError, not leak
    # into web3's JSON decoder as JSONDecodeError('').
    with pytest.raises(ClientResponseError) as exc_info:
        await _post(_response(429, b"", reason="Too Many Requests"))
    assert exc_info.value.status == 429
    assert "Too Many Requests" in exc_info.value.message


async def test_error_status_with_html_body_raises():
    with pytest.raises(ClientResponseError) as exc_info:
        await _post(_response(502, b"<html>Bad Gateway</html>", reason="Bad Gateway"))
    assert exc_info.value.status == 502
    assert "<html>Bad Gateway</html>" in exc_info.value.message
