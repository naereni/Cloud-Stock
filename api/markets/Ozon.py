import asyncio
from datetime import datetime, timedelta

from api.markets.MetaMarket import Market
from api.utils import CacheManager, asave_product, logger, tglog
from config.api_config import Ozon_config
from config.django_config import DJANGO_DEBUG


class Ozon(Market):
    def __init__(self):
        super().__init__(
            market="Ozon",
            base_url="https://api-seller.ozon.ru/" if not DJANGO_DEBUG else "http://127.0.0.1:8080/ozon/",
            headers={
                "Client-Id": Ozon_config.client_id,
                "Api-Key": Ozon_config.key,
            },
        )

        self.status_map = {
            "awaiting_packaging": ("OzonNew", lambda qty: (qty, qty)),
            "delivered": ("OzonComplited", lambda qty: (0, -qty)),
            "cancelled": ("OzonCancelled", lambda qty: (-qty, -qty)),
            "seller": ("OzonCancelled-seller", lambda qty: (-qty, -qty)),
            "client": ("OzonCancelled-client", lambda qty: (-qty, -qty)),
            "customer": ("OzonCancelled-customer", lambda qty: (-qty, -qty)),
            "delivery": ("OzonCancelled-delivery", lambda qty: (-qty, -qty)),
        }

    async def poll(self):
        await asyncio.gather(
            self.process_orders(),
            # self.process_returned()
        )
        self.cache.clean()

    async def process_orders(self, first_time=False):
        endpoint = "v3/posting/fbs/list"

        date_to = datetime.now()
        date_from = (date_to - timedelta(days=2)).strftime("%Y-%m-%dT%H:%M:%SZ")
        date_to = date_to.strftime("%Y-%m-%dT%H:%M:%SZ")

        request_data = {
            "dir": "ASC",
            "filter": {
                "since": date_from,
                "to": date_to,
            },
            "limit": 100,
        }

        responce = await self._apost(endpoint, request_data)

        for order in responce.get("result", []).get("postings", []):
            status, operation = self.status_map.get(order["status"], (False, lambda x: 0))
            if order.get("cancellation", None) is not None:
                status, operation = self.status_map.get(order.get("cancellation", None).get("cancellation_type", None), (False, lambda x: 0))
            # ID+status to avoid duplicate caches
            if status and not self.cache.check(str(order["order_id"]) + status) and not first_time:
                logger.info(f"{status} {order}")
                for item in order["products"]:
                    qty, res = operation(item["quantity"])
                    await asave_product(
                        service=status,
                        filters={
                            "ozon_warehouse": order["delivery_method"]["warehouse_id"],
                            "ozon_sku": item["sku"],
                        },
                        quantity=item["quantity"],
                        ozon_reserved=res,
                    )

    async def process_returned(self):
        endpoint = "v1/returns/list"

        date_to = datetime.now()
        date_from = (date_to - timedelta(days=2)).strftime("%Y-%m-%dT%H:%M:%SZ")
        date_to = date_to.strftime("%Y-%m-%dT%H:%M:%SZ")

        request_data = {
            "filter": {
                "since": date_from,
                "to": date_to,
                "visual_status_name": "ReceivedBySeller",
            },
            "limit": 100,
        }

        responce = await self._apost(endpoint, request_data)

        for order in ozon_returned_orders.get("returns", []):
            # Костыль чтобы в логах при отключенном prefill не светилось
            if order["product"]["sku"] == 1030404857 or order["product"]["sku"] == 1277480334:
                continue

            if not self.cache.check(str(order["order_id"])):
                logger.info(f"OzonReject {order}")
                for item in order["products"]:
                    await asave_product(
                        service="OzonReject",
                        filters={
                            "ozon_warehouse": order["delivery_method"]["warehouse_id"],
                            "ozon_sku": item["sku"],
                        },
                        quantity=-int(item["quantity"]),
                    )

    async def push_stocks(self, stocks_data: list[dict]):
        endpoint = "v2/products/stocks"
        try:
            _ = stocks_data[0].get("product_id")
        except Exception as e:
            logger.error(f"While pushing ozon stocks: {e}")
        request_data = {"stocks": stocks_data}

        responce = await self._post(endpoint, request_data)
        

    def get_stocks(self, skus: list):
        endpoint = "v1/product/info/stocks-by-warehouse/fbs"
        request_data = {"sku": skus}
        return self._post(endpoint, request_data)

    def get_warehouses(self):
        endpoint = "v1/warehouse/list"
        r = self._post(endpoint)
        return [{"warehouse_id": house["warehouse_id"], "name": house["name"]} for house in r["result"]]


# async def main():
#     ozon = Ozon()
#     r = await ozon.pull_orders()
#     print("$$$$$$$$$",r)
# import asyncio
# asyncio.run(main())
