import json
from datetime import datetime, timedelta

import requests

from api.utils.session_manager import SessionManager
from config.api_config import Ozon_config
from config.django_config import DJANGO_DEBUG


class Ozon:
    def __init__(self) -> None:
        self.headers = {
            "Client-Id": Ozon_config.client_id,
            "Api-Key": Ozon_config.key,
        }
        self.base_url = "https://api-seller.ozon.ru" if not DJANGO_DEBUG else "http://127.0.0.1:8080"
    
    async def pull_new_orders(self):
        session = await SessionManager.get_session()
        url = self.base_url+"/v3/posting/fbs/list"
        date_to = datetime.now()
        date_from = (date_to - timedelta(minutes=10)).strftime("%Y-%m-%dT%H:%M:%SZ")
        date_to = date_to.strftime("%Y-%m-%dT%H:%M:%SZ")

        request_data = {
            "dir": "ASC",
            "filter": {
                "since": date_from,
                "to": date_to,
                "status": "awaiting_deliver",
            },
            "limit": 100,
        }

        async with session.post(url, headers=self.headers, json=request_data) as response:
            return await response.json()
        
    def pull_new_orders_sync(self):
        url = self.base_url+"/v3/posting/fbs/list"
        date_to = datetime.now()
        date_from = (date_to - timedelta(minutes=10)).strftime("%Y-%m-%dT%H:%M:%SZ")
        date_to = date_to.strftime("%Y-%m-%dT%H:%M:%SZ")

        request_data = {
            "dir": "ASC",
            "filter": {
                "since": date_from,
                "to": date_to,
                "status": "awaiting_deliver",
            },
            "limit": 100,
        }

        response = requests.post(url, headers=self.headers, json=request_data)
        return response.json()

    async def pull_reserved(self):
        session = await SessionManager.get_session()
        url = self.base_url+"/v3/posting/fbs/list"
        date_to = datetime.now()
        date_from = (date_to - timedelta(minutes=10)).strftime("%Y-%m-%dT%H:%M:%SZ")
        date_to = date_to.strftime("%Y-%m-%dT%H:%M:%SZ")

        request_data = {
            "dir": "ASC",
            "filter": {
                "since": date_from,
                "to": date_to,
                "status": "delivering",
            },
            "limit": 100,
        }

        async with session.post(url, headers=self.headers, json=request_data) as response:
            return await response.json()

    async def pull_returned(self):
        session = await SessionManager.get_session()
        url = self.base_url+"/v1/returns/list"
        date_to = datetime.now()
        date_from = (date_to - timedelta(minutes=10)).strftime("%Y-%m-%dT%H:%M:%SZ")
        date_to = date_to.strftime("%Y-%m-%dT%H:%M:%SZ")

        request_data = {
            "dir": "ASC",
            "filter": {
                "since": date_from,
                "to": date_to,
                "status": "ReceivedBySeller",
            },
            "limit": 100,
        }
        async with session.post(url, headers=self.headers, json=request_data) as response:
            return await response.json()

    def get_stocks(self, skus: list):
        url = self.base_url+"/v1/product/info/stocks-by-warehouse/fbs"
        request_data = {"sku": skus}

        response = requests.post(url, headers=self.headers, json=request_data).json()
        return response["result"]

    async def aget_stocks(self, skus: list):
        session = await SessionManager.get_session()
        url = self.base_url+"/v1/product/info/stocks-by-warehouse/fbs"
        request_data = {"sku": skus}

        async with session.post(url, headers=self.headers, json=request_data) as response:
            result = await response.json()
            return result["result"]

    def get_warehouses(self):
        url = self.base_url+"/v1/warehouse/list"
        r = requests.post(url, headers=self.headers).json()
        houses = [{"warehouse_id": house["warehouse_id"], "name": house["name"]} for house in r["result"]]
        return houses


ozon = Ozon()
