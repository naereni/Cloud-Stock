import requests
import json
from config.api_config import Ymarket_config
from api.utils.session_manager import SessionManager


class Ymarket:
    def __init__(self) -> None:
        self.headers = {
            "Authorization": f"Bearer {Ymarket_config.key}",
            "Content-Type": "application/json",
        }
        self.business_id = Ymarket_config.business_id

    async def pull_returned_orders(self, campaign_id):
        session = await SessionManager.get_session()
        url = f"https://api.partner.market.yandex.ru/v2/campaigns/{campaign_id}/orders.json"
        params = {"status": "RETURNED"}
        async with session.get(url, headers=self.headers, params=params) as response:
            return await response.json()

    async def pull_reserved(self, campaign_id):
        session = await SessionManager.get_session()
        url = f"https://api.partner.market.yandex.ru/v2/campaigns/{campaign_id}/orders.json"
        params = {"status": "PROCESSING", "substatus": "STARTED"}
        async with session.get(url, headers=self.headers, params=params) as response:
            return await response.json()

    async def pull_new_orders(self, campaign_id):
        session = await SessionManager.get_session()
        url = f"https://api.partner.market.yandex.ru/v2/campaigns/{campaign_id}/orders.json"
        params = {"status": "DELIVERED"}
        async with session.get(url, headers=self.headers, params=params) as response:
            return await response.json()

    async def pull_stocks(self, campaign_id, skus: list):
        session = await SessionManager.get_session()
        url = f"https://api.partner.market.yandex.ru/v2/campaigns/{campaign_id}/offers/stocks.json"
        payload = {"offerIds": skus}
        async with session.post(url, headers=self.headers, json=payload) as response:
            result = await response.json()
            return result

    def get_warehouses(self):
        url = f"https://api.partner.market.yandex.ru/v2/businesses/{self.business_id}/warehouses.json"
        r = requests.get(url, headers=self.headers).json()
        houses = []
        for house in r["result"]["warehouses"]:
            houses.append(
                {
                    "warehouse_id": house["campaignId"],
                    "name": house["name"],
                }
            )
        return houses

    def check_product_in_warehouse(self, sku, campaign_id):
        url = f"https://api.partner.market.yandex.ru/v2/campaigns/{campaign_id}/offers/stocks"
        params = {"offer_id": sku, "warehouse_id": campaign_id}
        response = requests.get(url, headers=self.headers, params=params).json()
        for stock_info in response.get("result", {}).get("offers", []):
            if stock_info.get("warehouse_id") == campaign_id:
                return stock_info.get("count", 0) > 0
        return False

    # override
    async def test(self, *args, **kwargs):
        return json.loads(
            """
            [{
                "orders":[{
                    "id":572842730,
                    "status":"PROCESSING",
                    "substatus":"STARTED",
                    "items":[
                    {
                        "offerId":"Мила_140х200",
                        "count":1,
                    }
                }
            }]
        """
        )


ymarket = Ymarket()
