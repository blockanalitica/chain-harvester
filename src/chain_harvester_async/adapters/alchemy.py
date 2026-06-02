import os
from datetime import UTC, datetime
from decimal import Decimal

from chain_harvester_async.utils.http import retry_post_json

ALCHEMY_API_KEY = os.environ.get("ALCHEMY_RPC_KEY", "")


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


async def get_token_price(address, network, dt):
    network_mapping = {
        "ethereum": "eth-mainnet",
        "arbitrum": "arb-mainnet",
        "base": "base-mainnet",
        "monad": "monad-mainnet",
    }

    alchemy_network = network_mapping.get(network)
    if not alchemy_network:
        raise ValueError(
            f"Network '{network}' does not exists in our network mapping. "
            f"Supported: {', '.join(network_mapping.keys())}"
        )

    url = f"https://api.g.alchemy.com/prices/v1/{ALCHEMY_API_KEY}/tokens/historical"

    dt = datetime.combine(dt, datetime.min.time(), tzinfo=UTC)
    start_time = dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    end_time = start_time

    payload = {
        "address": address,
        "network": alchemy_network,
        "startTime": start_time,
        "endTime": end_time,
        "interval": "1d",
    }
    resp = await retry_post_json(
        url,
        json=payload,
        timeout=10,
        retries=0,
        raise_for_status=False,
        return_response=True,
    )

    if not resp:
        return

    resp_json = await resp.json()

    if err := resp_json.get("error", {}).get("message"):
        if "Token not found" in err:
            return None
        raise AlchemyClientError(err)

    data = resp_json.get("data", [])
    if len(data) > 0:
        price = Decimal(data[0]["value"])
        return price

    return
