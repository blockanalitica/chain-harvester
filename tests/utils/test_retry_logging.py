"""Retry logging must not publish credentials, and must not be a Sentry event.

Consumers install LoggingIntegration(event_level=WARNING), so a WARNING per
retried call published the URL's apikey as the issue title. See DATAHUB-6J.
"""

import logging

import aiohttp
import pytest

from chain_harvester_async.utils.http import retry_request_json

API_KEY = "K72AKUBWUYX8RCRXD17S4EC9NXQBF4HZVS"
URL = (
    "https://api.etherscan.io/v2/api?chainid=1&module=block"
    f"&action=getblocknobytime&timestamp=1789656076&apikey={API_KEY}"
)


class FakeResponse:
    """Enough of aiohttp's response to drive the retry loop."""

    def __init__(self, status, headers=None):
        self.status = status
        self.headers = headers or {}
        self.request_info = type("RequestInfo", (), {"real_url": URL, "url": URL})()
        self.history = ()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False

    def raise_for_status(self):
        raise aiohttp.ClientResponseError(
            self.request_info, self.history, status=self.status, message="Forbidden"
        )


@pytest.fixture
def always_times_out(monkeypatch):
    def _request(self, method, url, **kwargs):
        raise TimeoutError

    monkeypatch.setattr(aiohttp.ClientSession, "request", _request)


@pytest.fixture
def responds(monkeypatch):
    def _install(status, headers=None):
        def _request(self, method, url, **kwargs):
            return FakeResponse(status, headers)

        monkeypatch.setattr(aiohttp.ClientSession, "request", _request)

    return _install


async def test_retry_log_does_not_contain_the_api_key(always_times_out, caplog):
    with caplog.at_level(logging.INFO), pytest.raises(TimeoutError):
        await retry_request_json("GET", URL, retries=2, backoff_factor=0)

    assert caplog.records, "expected the retry to be logged"
    for record in caplog.records:
        assert API_KEY not in record.getMessage()


async def test_the_logged_exception_does_not_leak_the_key(responds, caplog):
    """ClientResponseError's repr embeds the URL it was raised for."""
    responds(403)
    with caplog.at_level(logging.INFO), pytest.raises(aiohttp.ClientResponseError):
        await retry_request_json("GET", URL, retries=1, backoff_factor=0)

    assert caplog.records, "expected the retry to be logged"
    for record in caplog.records:
        assert API_KEY not in record.getMessage()


async def test_retry_log_keeps_the_non_secret_query_params(always_times_out, caplog):
    with caplog.at_level(logging.INFO), pytest.raises(TimeoutError):
        await retry_request_json("GET", URL, retries=1, backoff_factor=0)

    message = caplog.records[0].getMessage()
    assert "action=getblocknobytime" in message
    assert "chainid=1" in message


async def test_recoverable_retries_are_logged_below_warning(always_times_out, caplog):
    """Anything at WARNING or above becomes a Sentry event; retries must not."""
    with caplog.at_level(logging.INFO), pytest.raises(TimeoutError):
        await retry_request_json("GET", URL, retries=3, backoff_factor=0)

    assert [r.levelno for r in caplog.records] == [logging.INFO] * 3


async def test_exhausted_429_retries_raise_instead_of_returning_none(responds, caplog):
    """A rate-limited endpoint must stay visible, not return None silently."""
    responds(429, {"Retry-After": "0"})
    with caplog.at_level(logging.INFO), pytest.raises(aiohttp.ClientResponseError):
        await retry_request_json("GET", URL, retries=2, backoff_factor=0)

    assert API_KEY not in caplog.text


async def test_the_429_retry_log_does_not_leak_the_key(responds, caplog):
    responds(429, {"Retry-After": "0"})
    with caplog.at_level(logging.INFO), pytest.raises(aiohttp.ClientResponseError):
        await retry_request_json("GET", URL, retries=1, backoff_factor=0)

    assert caplog.records, "expected the Retry-After branch to be logged"
    assert API_KEY not in caplog.text
