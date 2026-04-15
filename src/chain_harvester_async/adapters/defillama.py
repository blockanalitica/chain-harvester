import logging
from decimal import Decimal

from chain_harvester.utils import chunks
from chain_harvester_async.utils.http import retry_get_json

LLAMA_COINS_API_URL = "https://coins.llama.fi/"

log = logging.getLogger(__name__)


async def fetch_current_price(coins):
    """
    Fetches current prices for given coins from DefiLlama API.

    Args:
        coins (list): List of coins in format 'network:address'

    Returns:
        dict: Price data for requested coins
    """
    url = "prices/current/{}".format(",".join(coins))
    data = await retry_get_json(f"{LLAMA_COINS_API_URL}{url}?searchWidth=12h")
    return data["coins"]


async def get_current_prices(addresses, network="ethereum"):
    """
    Gets current prices for multiple token addresses on specified network.

    Args:
        addresses (list): List of token addresses
        network (str, optional): Blockchain network name. Defaults to "ethereum"

    Returns:
        dict: Price data for requested tokens
    """
    coins = [f"{network}:{address}" for address in addresses]
    data = await fetch_current_price(coins)

    result = {}
    if not data:
        return result
    for key, item in data.items():
        address = key.split(":")[1].lower()
        result[address] = Decimal(str(item["price"]))
    return result


async def get_price_for_timestamp(address, timestamp, network="ethereum"):
    """
    Gets historical price for a single token address at specific timestamp.

    Args:
        address (str): Token address
        timestamp (int): Unix timestamp
        network (str, optional): Blockchain network name. Defaults to "ethereum"

    Returns:
        Decimal: Token price at timestamp, returns 0 if price not found
    """
    prices = await get_tokens_price_for_timestamp([address], timestamp, network)
    if price := prices.get(address):
        return Decimal(str(price))
    return Decimal("0")


async def fetch_tokens_price_for_timestamp(timestamp, coins):
    """
    Fetches historical prices for given coins at specific timestamp from DefiLlama API.

    Args:
        timestamp (int): Unix timestamp
        coins (list): List of coins in format 'network:address'

    Returns:
        dict: Historical price data for requested coins
    """
    url = "prices/historical/{}/{}".format(int(timestamp), ",".join(coins))
    data = await retry_get_json(f"{LLAMA_COINS_API_URL}{url}?searchWidth=12h")
    return data["coins"]


async def get_tokens_price_for_timestamp(addresses, timestamp, network="ethereum"):
    """
    Gets historical prices for multiple token addresses at specific timestamp.

    Args:
        addresses (list): List of token addresses
        timestamp (int): Unix timestamp
        network (str, optional): Blockchain network name. Defaults to "ethereum"

    Returns:
        dict: Mapping of token addresses to their prices at timestamp
    """
    coins = [f"{network}:{address}" for address in addresses]
    data = await fetch_tokens_price_for_timestamp(timestamp, coins)
    result = {}
    if not data:
        return result
    for key, item in data.items():
        address = key.split(":")[1].lower()
        result[address] = Decimal(str(item["price"]))
    return result


async def get_tokens_price(addresses, timestamp, network="ethereum"):
    """
    Gets historical prices for a large list of token addresses, processing them in
    chunks.

    Args:
        addresses (list): List of token addresses
        timestamp (int): Unix timestamp
        network (str, optional): Blockchain network name. Defaults to "ethereum"

    Returns:
        dict: Mapping of token addresses to their prices at timestamp
    """
    prices = {}
    for chunk in chunks(addresses, 100):
        results = await get_tokens_price_for_timestamp(chunk, timestamp, network=network)
        prices.update(results)
    return prices


async def get_closest_block_before_timestamp(chain, timestamp):
    url = f"{LLAMA_COINS_API_URL}block/{chain.chain}/{timestamp}"
    response = await retry_get_json(url)
    block_number = response["height"]
    block_ts = response["timestamp"]
    tries = 0
    while block_ts > timestamp:
        if tries > 5:
            log.error(
                "Couldn't find closest block before %s. Using %s as closest alternative",
                timestamp,
                block_number,
            )
            break
        block_number -= 1
        block = await chain.get_block_info(block_number)
        block_ts = block["timestamp"]
        tries += 1

    return block_number
