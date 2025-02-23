import asyncio

from api.markets import ozon, wb, ymarket
from api.utils import CacheManager, asave_product, logger, tglog
from config.wh import y_whs


class ReturnPoller:
    def __init__(self):
        self.cache = CacheManager("Return cache")

    async def fetch_ozon_returns(self):
        try:
            ozon_returned_orders = await ozon.pull_returned()
            for order in ozon_returned_orders.get("returns", []):
                # Костыль
                if order["product"]["sku"] == 1030404857 or \
                   order["product"]["sku"] == 1277480334:
                    continue

                if not self.cache.check(order["order_id"]):
                    logger.info(f"$$$ REO {order}")
                    await asave_product(
                        service="RTO",
                        filters={"ozon_warehouse": order["place"]["id"], "ozon_sku": order["product"]["sku"]},
                        quantity=order["product"]["quantity"]
                    )
        except Exception as e:
            logger.error(f"RTO - {str(e)}")

    async def fetch_ymarket_returns(self):
        try:
            tasks = [ymarket.pull_returned(campaign_id) for campaign_id in y_whs]
            ymarket_returned_orders = await asyncio.gather(*tasks, return_exceptions=True)
            for i, city_orders in enumerate(ymarket_returned_orders):
                for order in city_orders.get("orders", []):
                    if not self.cache.check(order["id"]):
                        logger.info(f"$$$ REY {order}")
                        for item in order.get("items", []):
                            await asave_product(
                                service="REY",
                                filters={"y_warehouse": y_whs[i], "y_sku": item["offerId"]},
                                quantity=item["count"],
                            )
        except Exception as e:
            logger.error(f"RTY - {str(e)}")

    async def fetch_wb_returns(self):
        try:
            wb_orders_results = await wb.pull_orders()
            wb_orders_results = await wb.pull_orders_status(wb_orders_results)

            for order in wb_orders_results.get("orders", []):
                if self.cache.check(order["id"]) and order["wbStatus"] == "canceled":
                    logger.info(f"$$$ REW {order}")
                    for sku in order["skus"]:
                        await asave_product(
                            service="REW",
                            filters={"wb_warehouse": order["warehouseId"], "wb_sku": sku},
                            quantity=1,
                        )
        except Exception as e:
            logger.error(f"RTW - {str(e)}")

    async def poll(self):
        await asyncio.gather(
            self.fetch_ozon_returns(),
            self.fetch_ymarket_returns(),
            self.fetch_wb_returns(),
        )
        self.cache.end_cycle()
