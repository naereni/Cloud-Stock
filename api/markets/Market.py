import asyncio
from urllib.parse import urljoin

import aiohttp
import requests
from asgiref.sync import async_to_sync


class Market:
    def __init__(self, base_url="http://127.0.0.1:8080", headers={}):
        self.base_url = base_url
        self.headers = headers
        self._session = None

    async def get_session(self):
        if self._session is None:
            self._session = await aiohttp.ClientSession().__aenter__()
        # TODO проверить корректность создания сессии
        # print(self._session)
        return self._session

    async def close_session(self):
        if self._session is not None:
            await self._session.__aexit__(None, None, None)
            self._session = None

    async def _apost(self, endpoint, request_data=None):
        session = await self.get_session()
        async with session.post(
            urljoin(self.base_url, endpoint), headers=self.headers, json=request_data
        ) as response:
            return await response.json()

    async def _aget(self, endpoint, request_data=None):
        session = await self.get_session()
        async with session.get(
            urljoin(self.base_url, endpoint), headers=self.headers, params=request_data
        ) as response:
            return await response.json()

    def _post(self, endpoint, request_data=None):
        return requests.post(
            urljoin(self.base_url, endpoint), headers=self.headers, data=request_data
        ).json()

    def _get(self, endpoint, request_data=None):
        return requests.get(
            urljoin(self.base_url, endpoint), headers=self.headers, params=request_data
        ).json()

    # def __del__(self):
    #     asyncio.run(self.close_session())
