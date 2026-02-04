from asyncio import gather

from chain_harvester.constants import NO_STATE_OVERRIDE


def state_override_supported(chain_id):
    return chain_id not in NO_STATE_OVERRIDE


async def gather_raise(coroutines):
    results = await gather(*coroutines, return_exceptions=True)
    for obj in results:
        if isinstance(obj, Exception):
            raise obj

    return results
