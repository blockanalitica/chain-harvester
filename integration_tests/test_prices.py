from chain_harvester.prices import get_tokens_price
from integration_tests.constants import USDS_CONTRACT


async def test_get_tokens_price(chain):
    prices = await get_tokens_price([USDS_CONTRACT], 1763949167, "ethereum")
    assert USDS_CONTRACT in prices
