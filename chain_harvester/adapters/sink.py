from chain_harvester.http import retry_get_json
import urllib.parse

SINK_API_URL = "https://sink.blockanalitica.com/api/"


SUPPORTED_CHAINS = {
    "arbitrum",
    "avalanche",
    "base",
    "ethereum",
    "gnosis",
    "optimism",
}


def supports_chain(chain):
    return chain in SUPPORTED_CHAINS


def fetch_nearest_block(chain, timestamp, direction="before"):
    """
    Fetches blocks that's nearest to the timestamp based on direction
    """
    query_params = {
        "network": chain,
        "timestamp": timestamp,
        "direction": direction,
    }
    url = f"{SINK_API_URL}blocks/nearest/?{urllib.parse.urlencode(query_params)}"

    data = retry_get_json(url)
    return data["block_number"]
