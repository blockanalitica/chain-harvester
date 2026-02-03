from decimal import Decimal

from chain_harvester_async.adapters.defillama import (
    fetch_current_price,
    fetch_tokens_price_for_timestamp,
    get_current_prices,
    get_price_for_timestamp,
    get_tokens_price,
    get_tokens_price_for_timestamp,
)
from integration_tests.constants import USDS_CONTRACT


async def test_get_tokens_price():
    prices = await get_tokens_price([USDS_CONTRACT], 1763949167, "ethereum")
    assert USDS_CONTRACT in prices


async def test_get_tokens_price_for_timestamp():
    prices = await get_tokens_price_for_timestamp([USDS_CONTRACT], 1763949167, "ethereum")
    assert USDS_CONTRACT in prices


async def test_fetch_tokens_price_for_timestamp():
    coin = f"ethereum:{USDS_CONTRACT}"
    prices = await fetch_tokens_price_for_timestamp(1763949167, [coin])
    assert coin in prices


async def test_get_price_for_timestamp():
    price = await get_price_for_timestamp(USDS_CONTRACT, 1763949167, "ethereum")
    assert price == Decimal("0.9995702500439979")


async def test_get_current_prices():
    prices = await get_current_prices([USDS_CONTRACT], "ethereum")
    assert USDS_CONTRACT in prices


async def test_fetch_current_price():
    coin = f"ethereum:{USDS_CONTRACT}"
    prices = await fetch_current_price([coin])
    assert coin in prices
