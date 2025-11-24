from asyncio import gather as _gather

from chain_harvester.constants import NO_STATE_OVERRIDE


def state_override_supported(chain_id):
    return chain_id not in NO_STATE_OVERRIDE


async def gather(coroutines):
    results = await _gather(*coroutines, return_exceptions=True)
    for obj in results:
        if isinstance(obj, Exception):
            raise obj

    return results
