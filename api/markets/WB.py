import asyncio

from celery import shared_task

from api.markets.MetaMarket import Market
from api.utils import CacheManager, asave_product, logger, tglog
from api.utils.logger import logger
from config.api_config import WB_config
from config.django_config import DJANGO_DEBUG


class WB(Market):
    def __init__(self) -> None:
        super().__init__(
            market="WB",
            base_url=(
                "https://marketplace-api.wildberries.ru/api/"
                if not DJANGO_DEBUG
                else "http://127.0.0.1:8080/wb"
            ),
            headers={
                "Authorization": WB_config.key,
                "Content-Type": "application/json",
            },
        )
        self.status_map = {
            "new": ("WbNew", (1, 1)),
            "deliver": ("WbDeliver", (0, 1)),
            "receive": ("WbComplited", (0, -1)),
            "cancel": ("WbCancelled", (-1, -1)),
        }

    async def poll(self):
        await asyncio.gather(
            self.process_orders(),
        )
        self.cache.clean()

    async def process_orders(self):
        endpoint = "v3/dbs/orders/new"

        orders_data = await self._aget(endpoint)
        orders_data = await self.pull_orders_status(orders_data)

        for order in orders_data["orders"]:
            status, operation = self.status_map.get(order["supplierStatus"], (False, (0, 0)))
            if status == "WbDeliver":
                @sync_to_async
                def update_product():
                    with atomic():
                        Product.objects.filter(y_warehouse=y_whs[i], y_sku=item["offerId"]).update(
                            y_reserved=F("y_reserved") + res
                        )

                await update_product()

    async def pull_orders_status(self, orders_data: dict):
        endpoint = "v3/dbs/orders/status"
        request_data = {"orders": [order["id"] for order in orders_data["orders"]]}
        if request_data["orders"] == []:
            return orders_data
        response = await self._apost(endpoint, request_data)

        try:
            status_map = {order["id"]: order for order in response["orders"]}

            for order in orders_data["orders"]:
                order_id = order["id"]
                if order_id in status_map:
                    order["supplierStatus"] = status_map[order_id].get("supplierStatus", "")
            return orders_data

        except Exception as e:
            logger.warning(f"Packet loss, endpoint={endpoint}, Exception={e}")
            return orders_data

    async def process_orders(self, first_time=False):
        endpoint = "v3/dbs/orders/new"

        orders_data = await self._aget(endpoint)
        orders_data = await self.pull_orders_status(orders_data)

        for order in orders_data["orders"]:
            status, operation = self.status_map.get(order["supplierStatus"], (False, (0, 0)))
            status == ""
            if status and not self.cache.check(str(order["id"]) + status) and not first_time:
                logger.info(f"{status} {order}")
                for sku in order["skus"]:
                    qty, res = operation()
                    await asave_product(
                        service=status,
                        filters={"wb_warehouse": order["warehouseId"], "wb_sku": sku},
                        quantity=qty,
                        wb_reserved=res,
                    )

    async def push_stocks(self, stocks):
        endpoint = "v3/stocks/{0}"
        print(stocks)
        tasks = [
            self._aput(endpoint.format(warehouse_id), {"stocks": stocks[warehouse_id]})
            for warehouse_id in stocks.keys()
        ]
        r = await asyncio.gather(*tasks)
        logger.info(f"Response from WB push - {r}")

    async def pull_stocks(self, warehouse_id, skus: list):
        endpoint = f"v3/stocks/{warehouse_id}"

        request_data = {"skus": skus}
        return await self._apost(endpoint, request_data)

    def get_warehouses(self):
        endpoint = "https://suppliers-api.wildberries.ru/api/v3/warehouses"

        response = self._get(endpoint)
        try:
            houses = []
            for house in response:
                houses.append(
                    {
                        "warehouse_id": house["officeId"],
                        "name": house["name"],
                    }
                )
            return houses
        except Exception as e:
            logger.warning(f"ERROR while get wb new whs, Unexpected content type: {response.text}")
