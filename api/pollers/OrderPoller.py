import asyncio

from api.markets import ozon, wb, ymarket
from api.utils import CacheManager, asave_product, logger, tglog
from config.wh import y_whs


class OrderPoller:
    def __init__(self):
        self.cache = CacheManager("Orders cache")

    async def poll_ozon_orders(self):
        ozon_orders_results = await ozon.pull_orders()
        for posting in ozon_orders_results["result"]["postings"]:
            if not self.cache.check(str(posting["order_id"])):
                for item in posting["products"]:
                    await asave_product(
                        service="ORO",
                        filters={
                            "ozon_warehouse": posting["delivery_method"]["warehouse_id"],
                            "ozon_sku": item["sku"],
                        },
                        quantity=item["quantity"],
                    )

    async def poll_ymarket_orders(self):
        tasks = [ymarket.pull_orders(campaign_id) for campaign_id in y_whs]
        
        ymarket_orders_results = await asyncio.gather(*tasks)
        for i, wh in enumerate(ymarket_orders_results):
            for order in wh["orders"]:
                if not self.cache.check(str(order["id"])):
                    for item in order["items"]:
                        await asave_product(
                            service="ORY",
                            filters={"y_warehouse": y_whs[i], "y_sku": item["offerId"]},
                            quantity=item["count"],
                        )

    async def poll_wb_orders(self):
        wb_orders_results = await wb.pull_orders()
        wb_orders_results = await wb.pull_orders_status(wb_orders_results)

        for order in wb_orders_results["orders"]:
            if not self.cache.check(str(order["id"])) and order["wbStatus"] == "sold":
                for sku in order["skus"]:
                    await asave_product(
                        service="ORW",
                        filters={"wb_warehouse": order["warehouseId"], "wb_sku": sku},
                        quantity=1,
                    )

    async def poll(self):
        await asyncio.gather(
            self.poll_ozon_orders(),
            self.poll_ymarket_orders(),
            self.poll_wb_orders(),
        )
        self.cache.end_cycle()
