from datetime import datetime, timedelta

from api.utils.session_manager import SessionManager
from config.api_config import Ozon_config
from config.django_config import DJANGO_DEBUG
from api.markets.Market import Market


class Ozon(Market):
    def __init__(self):
        super().__init__(
            base_url = "https://api-seller.ozon.ru" if not DJANGO_DEBUG else "http://127.0.0.1:8080/ozon/",
            headers = {
                "Client-Id": Ozon_config.client_id,
                "Api-Key": Ozon_config.key,
            }
        )

    async def pull_orders(self):
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

        return await self._post(url, request_data)



    async def pull_reserved(self):
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

        return await self._post(url, request_data)


    async def pull_returned(self):
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
        
        return await self._post(url, request_data)


    async def get_stocks(self, skus: list):
        url = self.base_url+"/v1/product/info/stocks-by-warehouse/fbs"
        request_data = {"sku": skus}
        return await self._post(url, request_data)


    def get_warehouses(self):
        url = self.base_url+"/v1/warehouse/list"
        r = self._post(url)
        houses = [{"warehouse_id": house["warehouse_id"], "name": house["name"]} for house in r["result"]]
        return houses


ozon = Ozon()
