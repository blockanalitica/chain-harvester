import os
from asyncio import Semaphore, new_event_loop, set_event_loop
from asyncio import gather as _gather
from asyncio import get_event_loop as _get_event_loop

from chain_harvester.constants import NO_STATE_OVERRIDE


def state_override_supported(chain_id):
    return chain_id not in NO_STATE_OVERRIDE


# -------------------------------------------------
# TODO: Is everything below this line necessary?
# NOTE: If we run too many async calls at once, we'll have memory issues.
#       Feel free to increase this with the "MULTICALL_CALL_SEMAPHORE" env var if you
#       know what you're doing.
ASYNC_SEMAPHORE = int(os.environ.get("MULTICALL_CALL_SEMAPHORE", 1000))


def get_event_loop():
    try:
        loop = _get_event_loop()
    except RuntimeError as e:  # Necessary for use with multi-threaded applications.
        if not str(e).startswith("There is no current event loop in thread"):
            raise
        loop = new_event_loop()
        set_event_loop(loop)
    return loop


_semaphores = {}


def _get_semaphore():
    """
    Returns a `Semaphore` attached to the current event loop.

    NOTE: This prevents an "attached to a different loop" edge case if the event loop
          is changed during your script run
    """
    loop = get_event_loop()
    try:
        return _semaphores[loop]
    except KeyError:
        semaphore = _semaphores[loop] = Semaphore(ASYNC_SEMAPHORE)
        return semaphore


def raise_if_exception(obj):
    if isinstance(obj, Exception):
        raise obj


def raise_if_exception_in(iterable):
    for obj in iterable:
        raise_if_exception(obj)


async def gather(coroutines):
    results = await _gather(*coroutines, return_exceptions=True)
    raise_if_exception_in(results)
    return results
