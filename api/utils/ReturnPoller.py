import asyncio

from asgiref.sync import sync_to_async
from django.core.exceptions import ObjectDoesNotExist

from api.services.Ozon import ozon
from api.services.WB import wb
from api.services.Ymarket import ymarket
from api.utils.CacheManager import CacheManager
from api.utils.logger import logger
from Cloud_Stock.models import Product
from config.wh import y_whs


class ReturnPoller:
    def __init__(self):
        self.cache = CacheManager("Return cache")

    async def save_return_to_db(self, warehouse_id: int, sku: str, quantity: int):
        cache_key = f"{warehouse_id}:{sku}"
        if not self.cache.is_in_cache(cache_key):
            try:
                obj = await Product.objects.aget(
                    ozon_warehouse=warehouse_id if hasattr(Product, "ozon_warehouse") else None,
                    wb_warehouse=warehouse_id if hasattr(Product, "wb_warehouse") else None,
                    y_warehouse=warehouse_id if hasattr(Product, "y_warehouse") else None,
                    ozon_sku=sku if hasattr(Product, "ozon_sku") else None,
                    y_sku=sku if hasattr(Product, "y_sku") else None,
                    wb_sku=sku if hasattr(Product, "wb_sku") else None,
                )
                obj.stock += quantity
                obj.is_modified = True
                obj.last_user = "RTP"
                await sync_to_async(obj.save)()
                logger.info(f"RTP: {obj.name}, new stock: {obj.stock}, SKU: {sku}")
            except ObjectDoesNotExist:
                logger.warning(f"RTP: Product not found for return order: SKU {sku}, Warehouse {warehouse_id}")

    async def fetch_ozon_returns(self):
        ozon_returned_orders = await ozon.pull_returned()
        for order in ozon_returned_orders.get("result", {}).get("postings", []):
            for item in order.get("products", []):
                await self.save_return_to_db(
                    warehouse_id=order["delivery_method"]["warehouse_id"],
                    sku=item["sku"],
                    quantity=item["quantity"],
                )

    async def fetch_ymarket_returns(self):
        tasks = [ymarket.pull_returned_orders(campaign_id) for campaign_id in y_whs]
        ymarket_returned_orders = await asyncio.gather(*tasks)
        for i, city_orders in enumerate(ymarket_returned_orders):
            for order in city_orders.get("orders", []):
                for item in order.get("items", []):
                    await self.save_return_to_db(
                        warehouse_id=y_whs[i],
                        sku=item["offerId"],
                        quantity=item["count"],
                    )

    async def fetch_wb_returns(self):
        wb_orders_results = await wb.pull_new_orders()
        wb_orders_results = await wb.pull_orders_status(wb_orders_results)

        for order in wb_orders_results.get("orders", []):
            if order["wbStatus"] == "canceled":
                for sku in order["skus"]:
                    await self.save_return_to_db(
                        warehouse_id=order["warehouseId"],
                        sku=sku,
                        quantity=1,
                    )

    async def poll(self):
        await asyncio.gather(
            self.fetch_ozon_returns(),
            self.fetch_ymarket_returns(),
            self.fetch_wb_returns(),
        )
        self.cache.finalize_cycle()


return_poller = ReturnPoller()
