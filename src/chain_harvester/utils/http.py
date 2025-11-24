import asyncio
import logging

import aiohttp

log = logging.getLogger(__name__)


async def retry_request_json(
    method,
    url,
    retries=3,
    timeout=30,
    backoff_factor=0.5,
    status_forcelist=(429, 500, 502, 503, 504),
    raise_for_status=True,
    **kwargs,
):
    """
    Retry backoff: {backoff factor} * (2 ** (attempt - 1)) seconds.
    Example with backoff_factor=0.5: [0, 1, 2, 4, ...] seconds.
    """
    client_timeout = aiohttp.ClientTimeout(total=timeout)
    async with aiohttp.ClientSession(timeout=client_timeout) as session:
        for attempt in range(retries + 1):
            try:
                async with session.request(method, url, **kwargs) as resp:
                    if resp.status in status_forcelist:
                        # Handle Retry-After if present (mostly for 429)
                        if resp.status == 429:
                            retry_after = resp.headers.get("Retry-After")
                            if retry_after is not None:
                                log.warning(
                                    (
                                        "Received 429 with Retry-After=%s on url %s. "
                                        "Sleeping..."
                                    ),
                                    int(retry_after),
                                    url,
                                )
                                await asyncio.sleep(int(retry_after))
                                continue

                        if attempt < retries:
                            delay = backoff_factor * (2 ** (attempt))
                            await asyncio.sleep(delay)
                            continue

                    if raise_for_status:
                        resp.raise_for_status()
                    return await resp.json()
            except (asyncio.TimeoutError, aiohttp.ClientError) as e:
                err_type = (
                    "TimeoutError"
                    if isinstance(e, asyncio.TimeoutError)
                    else "ClientError"
                )
                if attempt < retries:
                    delay = backoff_factor * (2 ** (attempt))
                    log.warning(
                        (
                            "%s while requesting %s: %s. Retrying in %s seconds "
                            "(attempt %s/%s)..."
                        ),
                        err_type,
                        url,
                        e,
                        delay,
                        attempt + 1,
                        retries,
                    )
                    await asyncio.sleep(delay)
                    continue
                raise


async def retry_get_json(url, **kwargs):
    return await retry_request_json("GET", url, **kwargs)


async def retry_post_json(url, **kwargs):
    return await retry_request_json("POST", url, **kwargs)
