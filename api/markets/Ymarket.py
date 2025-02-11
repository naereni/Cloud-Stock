from api.markets.MetaMarket import Market
from config.api_config import Ymarket_config
from config.django_config import DJANGO_DEBUG


class Ymarket(Market):
    def __init__(self):
        super().__init__(
            base_url=(
                "https://api.partner.market.yandex.ru/" if not DJANGO_DEBUG else "http://127.0.0.1:8080/y"
            ),
            headers={
                "Authorization": f"Bearer {Ymarket_config.key}",
                "Content-Type": "application/json",
            },
        )
        self.business_id = Ymarket_config.business_id

    async def pull_orders(self, campaign_id):
        endpoint = f"v2/campaigns/{campaign_id}/orders"
        request_data = {"status": "DELIVERED"}
        return await self._aget(endpoint, request_data)

    async def pull_reserved(self, campaign_id):
        endpoint = f"v2/campaigns/{campaign_id}/orders"
        request_data = {"status": "PROCESSING", "substatus": "STARTED"}
        return await self._aget(endpoint, request_data)

    async def pull_returned(self, campaign_id):
        endpoint = f"v2/campaigns/{campaign_id}/orders"
        request_data = {"status": "RETURNED"}
        return await self._aget(endpoint, request_data)

    async def pull_stocks(self, campaign_id, skus: list):
        endpoint = f"v2/campaigns/{campaign_id}/offers/stocks"
        request_data = {"offerIds": skus}
        return await self._apost(endpoint, request_data)

    def get_warehouses(self):
        endpoint = f"v2/businesses/{self.business_id}/warehouses"
        r = self._get(endpoint)
        return [
            {"warehouse_id": house["campaignId"], "name": house["name"]}
            for house in r["result"]["warehouses"]
        ]


# async def main():
#     ymarket = Ymarket()
#     r = await ymarket.pull_returned_orders("131709783")
#     print("$$$$$$$$$",r)
# import asyncio
# asyncio.run(main())
