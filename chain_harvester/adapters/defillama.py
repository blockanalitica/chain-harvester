from decimal import Decimal

from ..utils import chunks
from ..utils.http import retry_get_json

LLAMA_COINS_API_URL = "https://coins.llama.fi/"


def fetch_current_price(coins):
    url = "prices/current/{}/".format(",".join(coins))
    data = retry_get_json(f"{LLAMA_COINS_API_URL}{url}?searchWidth=12h")
    return data["coins"]


def fetch_price_for_timestamp(timestamp, coins):
    url = "prices/historical/{}/{}/".format(int(timestamp), ",".join(coins))
    data = retry_get_json(f"{LLAMA_COINS_API_URL}{url}?searchWidth=12h")
    return data["coins"]


def get_current_prices(addresses, network="ethereum"):
    coins = [f"{network}:{address}" for address in addresses]
    data = fetch_current_price(coins)
    return data


def get_prices_for_timestamp(timestamp, addresses, network="ethereum"):
    coins = [f"{network}:{address}" for address in addresses]
    data = fetch_price_for_timestamp(timestamp, coins)
    result = {}
    if not data:
        return result
    for key, item in data.items():
        address = key.split(":")[1].lower()
        price = item["price"]
        result[address] = price
    return result


def get_price_for_timestamp(timestamp, address, network="ethereum"):
    prices = get_prices_for_timestamp(timestamp, [address], network)
    if price := prices.get(address):
        return Decimal(str(price))
    return Decimal(0)


def get_token_prices(addresses, timestamp, network="ethereum"):
    prices = {}
    for chunk in chunks(addresses, 100):
        results = get_prices_for_timestamp(
            timestamp,
            addresses=chunk,
            network=network,
        )
        prices.update(results)
    return prices
