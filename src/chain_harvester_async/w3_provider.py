from web3 import AsyncHTTPProvider
from web3._utils.http_session_manager import HTTPSessionManager


class CustomHTTPSessionManager(HTTPSessionManager):
    async def async_make_post_request(self, endpoint_uri, data, **kwargs):
        # We override this function to remove `response.raise_for_status()` so we get
        # better errors
        response = await self.async_get_response_from_post_request(
            endpoint_uri, data=data, **kwargs
        )
        return await response.read()


class CustomAsyncHTTPProvider(AsyncHTTPProvider):
    def __init__(self, *args, request_kwargs=None, **kwargs):
        super().__init__(*args, request_kwargs=request_kwargs, **kwargs)
        self._request_session_manager = CustomHTTPSessionManager()
