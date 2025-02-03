import aiohttp
from asgiref.sync import async_to_sync


class Market:
    def __init__(self, base_url="http://127.0.0.1:8080", headers={}):
        self.base_url = base_url
        self.headers = headers
        self._session = async_to_sync(self._init_session)()

    async def _init_session(self):
        self._session = await aiohttp.ClientSession().__aenter__()
        return self

    async def _post(self, url, request_data=None):
        async with self._session.post(url, headers=self.headers, json=request_data) as response:
            return await response.json()

    async def _get(self, url, request_data=None):
        async with self._session.get(url, headers=self.headers, params=request_data) as response:
            return await response.json()

    async def _close_session(self):
        if self._session is not None:
            await self._session.__aexit__(None, None, None)
            self._session = None

    def __del__(self):
        if self._session is not None:
            async_to_sync(self._close_session)()