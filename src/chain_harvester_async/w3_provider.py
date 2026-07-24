import json

from aiohttp import ClientResponseError
from web3 import AsyncHTTPProvider
from web3._utils.http_session_manager import HTTPSessionManager


def _is_json(body):
    try:
        json.loads(body)
    except (ValueError, UnicodeDecodeError):
        return False
    return True


class CustomHTTPSessionManager(HTTPSessionManager):
    async def async_make_post_request(self, endpoint_uri, data, **kwargs):
        # Web3's stock session manager calls `response.raise_for_status()`, which
        # discards the body — but some RPCs return JSON-RPC error payloads with a
        # non-200 status, and those must reach web3's decoder so the caller sees the
        # RPC's actual error. An error status WITHOUT a JSON body (a bare 429/5xx
        # from a rate limiter or proxy) is different: passed through, it surfaces as
        # JSONDecodeError('') in the decoder and silently bypasses the provider's
        # ExceptionRetryConfiguration (which retries ClientError subclasses), so
        # raise it as the ClientResponseError it really is.
        response = await self.async_get_response_from_post_request(
            endpoint_uri, data=data, **kwargs
        )
        body = await response.read()
        if response.status >= 400 and not _is_json(body):
            snippet = body[:200].decode(errors="replace")
            raise ClientResponseError(
                response.request_info,
                response.history,
                status=response.status,
                message=f"{response.reason}; body={snippet!r}",
                headers=response.headers,
            )
        return body


class CustomAsyncHTTPProvider(AsyncHTTPProvider):
    def __init__(self, *args, request_kwargs=None, **kwargs):
        super().__init__(*args, request_kwargs=request_kwargs, **kwargs)
        self._request_session_manager = CustomHTTPSessionManager()
