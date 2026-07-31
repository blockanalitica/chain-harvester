import os
from datetime import UTC, datetime, timedelta
from decimal import Decimal

from chain_harvester_async.utils.http import retry_post_json

ALCHEMY_API_KEY = os.environ.get("ALCHEMY_RPC_KEY", "")

PRICE_NETWORKS = {
    "ethereum": "eth-mainnet",
    "arbitrum": "arb-mainnet",
    "base": "base-mainnet",
    "polygon": "polygon-mainnet",
    "optimism": "opt-mainnet",
    "unichain": "unichain-mainnet",
    "linea": "linea-mainnet",
    "scroll": "scroll-mainnet",
    "monad": "monad-mainnet",
}

# The historical endpoint rejects a 1d interval covering more than 365 points, so longer
# windows are requested one chunk at a time.
PRICE_SERIES_MAX_DAYS = 365

PRICE_TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%SZ"


class AlchemyClientError(Exception):
    pass


def _get_blocks_query(to_block=None):
    base_query = """
        query ($first: Int!, $skip: Int!, $from_block: Int!{to_block_var}) {{
            blocks (orderBy: number, first: $first, skip: $skip, where:
                {{number_gt: $from_block{to_block_filter}}}) {{
                number
                timestamp
                id
            }}
        }}
    """

    to_block_var = ", $to_block: Int!" if to_block is not None else ""
    to_block_filter = ", number_lte: $to_block" if to_block is not None else ""

    query = base_query.format(to_block_var=to_block_var, to_block_filter=to_block_filter)
    return query


async def get_blocks(url, from_block, to_block=None, limit=10000, timeout=30, retries=3):
    headers = {"accept": "application/json", "content-type": "application/json"}
    first = limit
    skip = 0
    while True:
        query = _get_blocks_query(to_block)

        payload = {
            "query": query,
            "variables": {
                "first": first,
                "skip": skip,
                "from_block": from_block,
                "to_block": to_block,
            },
        }
        response = await retry_post_json(
            url, json=payload, headers=headers, timeout=timeout, retries=retries
        )

        if not response.get("data", {}).get("blocks"):
            break

        for block in response["data"]["blocks"]:
            yield block

        skip += first


def _price_network(network):
    alchemy_network = PRICE_NETWORKS.get(network)
    if not alchemy_network:
        raise ValueError(
            f"Network '{network}' does not exists in our network mapping. "
            f"Supported: {', '.join(PRICE_NETWORKS.keys())}"
        )
    return alchemy_network


def _price_timestamp(dt):
    return datetime.combine(dt, datetime.min.time(), tzinfo=UTC).strftime(PRICE_TIMESTAMP_FORMAT)


async def _fetch_prices(address, alchemy_network, start, end):
    url = f"https://api.g.alchemy.com/prices/v1/{ALCHEMY_API_KEY}/tokens/historical"

    payload = {
        "address": address,
        "network": alchemy_network,
        "startTime": _price_timestamp(start),
        "endTime": _price_timestamp(end),
        "interval": "1d",
    }
    resp = await retry_post_json(
        url,
        json=payload,
        timeout=30,
        retries=3,
        raise_for_status=False,
        return_response=True,
    )

    if not resp:
        return []

    resp_json = await resp.json()

    if err := resp_json.get("error", {}).get("message"):
        if "Token not found" in err:
            return []
        raise AlchemyClientError(err)

    return resp_json.get("data", [])


async def get_token_price(address, network, dt):
    if network == "monad":
        # alchemy doesnt support monad ...
        return

    data = await _fetch_prices(address, _price_network(network), dt, dt)
    if data:
        return Decimal(data[0]["value"])

    return


async def get_token_price_series(address, network, start_date, end_date):
    if network == "monad":
        # alchemy doesnt support monad ...
        return {}

    alchemy_network = _price_network(network)
    prices = {}
    window_start = start_date
    while window_start <= end_date:
        window_end = min(
            window_start + timedelta(days=PRICE_SERIES_MAX_DAYS - 1),
            end_date,
        )
        for entry in await _fetch_prices(address, alchemy_network, window_start, window_end):
            day = datetime.fromisoformat(entry["timestamp"]).date()
            prices[day] = Decimal(entry["value"])
        window_start = window_end + timedelta(days=1)
    return prices
