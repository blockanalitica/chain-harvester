from chain_harvester.adapters import defillama


async def get_tokens_price(addresses, timestamp, network="ethereum"):
    return await defillama.get_tokens_price(addresses, timestamp, network)
