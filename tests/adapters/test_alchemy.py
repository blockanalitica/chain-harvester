from datetime import date
from decimal import Decimal
from unittest.mock import AsyncMock, patch

import pytest

from chain_harvester_async.adapters.alchemy import (
    AlchemyClientError,
    get_token_price,
    get_token_price_series,
)

USDC = "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48"


def make_response(body):
    response = AsyncMock()
    response.json.return_value = body
    return response


def point(day, value):
    return {"timestamp": f"2024-01-{day:02d}T00:00:00Z", "value": value}


async def test_get_token_price_returns_the_single_day_value():
    with patch(
        "chain_harvester_async.adapters.alchemy.retry_post_json",
        AsyncMock(return_value=make_response({"data": [point(1, "0.9992")]})),
    ):
        assert await get_token_price(USDC, "ethereum", date(2024, 1, 1)) == Decimal("0.9992")


async def test_get_token_price_returns_none_for_an_unpriced_token():
    body = {"error": {"message": "Token not found: 0xeee"}}
    with patch(
        "chain_harvester_async.adapters.alchemy.retry_post_json",
        AsyncMock(return_value=make_response(body)),
    ):
        assert await get_token_price(USDC, "ethereum", date(2024, 1, 1)) is None


async def test_get_token_price_raises_on_other_api_errors():
    body = {"error": {"message": "1d interval is limited to 365 days"}}
    with (
        patch(
            "chain_harvester_async.adapters.alchemy.retry_post_json",
            AsyncMock(return_value=make_response(body)),
        ),
        pytest.raises(AlchemyClientError),
    ):
        await get_token_price(USDC, "ethereum", date(2024, 1, 1))


@pytest.mark.parametrize(
    "network",
    ["polygon", "optimism", "unichain", "linea", "scroll"],
)
async def test_prices_resolve_on_the_networks_added_for_the_compound_reserves_backfill(network):
    post = AsyncMock(return_value=make_response({"data": [point(1, "1.0")]}))
    with patch("chain_harvester_async.adapters.alchemy.retry_post_json", post):
        assert await get_token_price(USDC, network, date(2024, 1, 1)) == Decimal("1.0")

    assert post.await_args.kwargs["json"]["network"].endswith("-mainnet")


async def test_unmapped_network_still_raises():
    with pytest.raises(ValueError, match="ronin"):
        await get_token_price(USDC, "ronin", date(2024, 1, 1))


async def test_price_series_keys_daily_values_by_date():
    body = {"data": [point(1, "0.9992"), point(2, "1.0012"), point(3, "1.0021")]}
    with patch(
        "chain_harvester_async.adapters.alchemy.retry_post_json",
        AsyncMock(return_value=make_response(body)),
    ):
        prices = await get_token_price_series(USDC, "ethereum", date(2024, 1, 1), date(2024, 1, 3))

    assert prices == {
        date(2024, 1, 1): Decimal("0.9992"),
        date(2024, 1, 2): Decimal("1.0012"),
        date(2024, 1, 3): Decimal("1.0021"),
    }


async def test_price_series_chunks_windows_past_the_365_point_cap():
    # The endpoint rejects a 1d interval spanning more than 365 points, so a multi-year
    # backfill window has to be requested in successive chunks.
    post = AsyncMock(return_value=make_response({"data": []}))
    with patch("chain_harvester_async.adapters.alchemy.retry_post_json", post):
        await get_token_price_series(USDC, "ethereum", date(2021, 1, 1), date(2023, 1, 1))

    windows = [
        (call.kwargs["json"]["startTime"], call.kwargs["json"]["endTime"])
        for call in post.await_args_list
    ]
    assert windows == [
        ("2021-01-01T00:00:00Z", "2021-12-31T00:00:00Z"),
        ("2022-01-01T00:00:00Z", "2022-12-31T00:00:00Z"),
        ("2023-01-01T00:00:00Z", "2023-01-01T00:00:00Z"),
    ]


async def test_price_series_is_empty_for_a_token_alchemy_does_not_price():
    body = {"error": {"message": "Token not found: 0xeee"}}
    with patch(
        "chain_harvester_async.adapters.alchemy.retry_post_json",
        AsyncMock(return_value=make_response(body)),
    ):
        prices = await get_token_price_series(USDC, "ethereum", date(2024, 1, 1), date(2024, 1, 3))

    assert prices == {}
