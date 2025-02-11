import traceback
from urllib.parse import urljoin

import requests
from aiohttp import ClientResponseError, ClientSession

from api.utils.logger import logger, tglog


class Market:
    def __init__(self, base_url="http://127.0.0.1:8080", headers={}):
        self.base_url = base_url
        self.headers = headers
        self._session = None

    async def get_session(self):
        if self._session is None:
            self._session = await ClientSession().__aenter__()
        # TODO проверить корректность создания сессии
        # print(self._session)
        return self._session

    async def close_session(self):
        if self._session is not None:
            await self._session.__aexit__(None, None, None)
            self._session = None

    async def _apost(self, endpoint, request_data=None):
        session = await self.get_session()
        url = urljoin(self.base_url, endpoint)

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
                return response.json()  # Убрали второй вызов .json()
            else:
                logger.error(f"_get to {url}: {response.status_code} - {response.text}")

        except requests.exceptions.RequestException as e:
            logger.exception(f"RequestException while _get to {url}: {e}")

    # def __del__(self):
    #     asyncio.run(self.close_session())
