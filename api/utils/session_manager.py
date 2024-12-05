import aiohttp


class SessionManager:
    _session = None

    @classmethod
    async def get_session(cls):
        if cls._session is None:
            cls._session = await aiohttp.ClientSession().__aenter__()
        return cls._session

    @classmethod
    async def close_session(cls):
        if cls._session is not None:
            await cls._session.__aexit__(None, None, None)
            cls._session = None
