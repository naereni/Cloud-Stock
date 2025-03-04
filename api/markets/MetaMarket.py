import asyncio
import traceback
from urllib.parse import urljoin

import requests
from aiohttp import ClientResponseError, ClientSession

from api.utils import CacheManager, logger


class Market:
    def __init__(self, market, base_url="http://127.0.0.1:8080", headers={}, max_concurrent_requests=1000):
        self.base_url = base_url
        self.headers = headers
        self._session = None
        self.semaphore = asyncio.Semaphore(max_concurrent_requests)
        self.cache = CacheManager(market)

    async def polling_cycle(self):
        await asyncio.gather(
            self.new_orders(),
            self.complited_orders(),
            self.cancelled_orders(),
            self.returned_orders(),
        )
        self.cache.clean()

    async def get_session(self):
        if self._session is None:
            self._session = await ClientSession().__aenter__()
        return self._session

    async def close_session(self):
        if self._session is not None:
            await self._session.__aexit__(None, None, None)
            self._session = None

    async def _aput(self, endpoint, request_data=None):
        print(request_data)
        session = await self.get_session()
        url = urljoin(self.base_url, endpoint)
        async with self.semaphore:
            try:
                async with session.put(url, headers=self.headers, json=request_data) as response:
                    if response.status == 200 and response.status == 204:
                        return await response.json()
                    else:
                        error_text = await response.text()
                        logger.error(f"_aput to {url}: {response.status} - {error_text}")
            except ClientResponseError as e:
                logger.exception(f"ClientResponseError while _aput {url}: {e.status} - {e.message}")

    async def _apost(self, endpoint, request_data=None):
        session = await self.get_session()
        url = urljoin(self.base_url, endpoint)

        async with self.semaphore:
            try:
                async with session.post(url, headers=self.headers, json=request_data) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        error_text = await response.text()
                        logger.error(f"_apost to {url}: {response.status} - {error_text}")
            except ClientResponseError as e:
                logger.exception(f"ClientResponseError while _apost {url}: {e.status} - {e.message}")

    async def _aget(self, endpoint, request_data=None):
        session = await self.get_session()
        url = urljoin(self.base_url, endpoint)

        async with self.semaphore:
            try:
                async with session.get(url, headers=self.headers, params=request_data) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        error_text = await response.text()
                        logger.error(f"_aget to {url}: {response.status} - {error_text}")
            except ClientResponseError as e:
                logger.exception(f"ClientResponseError while _aget {url}: {e.status} - {e.message}")

    def _post(self, endpoint, request_data=None):
        url = urljoin(self.base_url, endpoint)
        try:
            response = requests.post(url, headers=self.headers, json=request_data, timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"_post to {url}: {response.status_code} - {response.text}")
        except requests.exceptions.RequestException as e:
            logger.exception(f"RequestException while _post {url}: {e}")

    def _get(self, endpoint, request_data=None):
        url = urljoin(self.base_url, endpoint)
        try:
            response = requests.get(url, headers=self.headers, params=request_data)
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"_get to {url}: {response.status_code} - {response.text}")
        except requests.exceptions.RequestException as e:
            logger.exception(f"RequestException while _get to {url}: {e}")
