import asyncio

from api.markets import ozon, wb, ymarket
from api.utils import asave_product, zero_out_reserved
from config.wh import y_whs


class ReservePoller:
    async def pull_ozon_reserved(self):
        ozon_orders_results = await ozon.pull_reserved()

        for posting in ozon_orders_results["result"]["postings"]:
            for item in posting["products"]:
                await asave_product(
                    service="REO",
                    filters={
                        "ozon_warehouse": posting["delivery_method"]["warehouse_id"],
                        "ozon_sku": item["sku"],
                    },
                    quantity=item["quantity"],
                )

    async def pull_ymarket_reserved(self):
        tasks = [ymarket.pull_reserved(campaign_id) for campaign_id in y_whs]

        ymarket_orders_results = await asyncio.gather(*tasks)
        if ymarket_orders_results:
            for i, city in enumerate(ymarket_orders_results):
                for order in city["orders"]:
                    for item in order["items"]:
                        await asave_product(
                            service="REY",
                            filters={"y_warehouse": y_whs[i], "y_sku": item["offerId"]},
                            quantity=item["count"],
                        )

    async def pull_wb_reserved(self):
        wb_orders_results = await wb.pull_orders()
        wb_orders_results = await wb.pull_orders_status(wb_orders_results)

        for order in wb_orders_results["orders"]:
            if order["supplierStatus"] == "new":
                for sku in order["skus"]:
                    await asave_product(
                        service="REW",
                        filters={"wb_warehouse": order["warehouseId"], "wb_sku": sku},
                        quantity=1,
                    )

    async def poll(self):
        await asyncio.gather(
            zero_out_reserved(),
            self.pull_ozon_reserved(),
            self.pull_ymarket_reserved(),
            self.pull_wb_reserved(),
        )
