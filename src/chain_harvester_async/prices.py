from chain_harvester_async.adapters import alchemy, defillama


async def get_tokens_price(addresses, timestamp, network="ethereum"):
    return await defillama.get_tokens_price(addresses, timestamp, network)


async def get_alchemy_token_price(address, network, dt):
    return await alchemy.get_token_price(address, network, dt)
