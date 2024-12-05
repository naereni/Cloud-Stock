import asyncio
from api.services.Ozon import ozon
from api.services.Ymarket import ymarket
from api.services.WB import wb
from config.wh import y_whs, warehouses
from Cloud_Stock.models import Product
from api.utils.CacheManager import CacheManager
from asgiref.sync import sync_to_async
from django.core.exceptions import ObjectDoesNotExist
from api.utils.OrderPoller import logger


class ReservePoller:
    def __init__(self):
        self.cache = CacheManager("Reserve cache")

    async def pull_ymarket_reserved(self):
        tasks = [ymarket.pull_reserved(campaign_id) for campaign_id in y_whs]

        for obj in await sync_to_async(list)(Product.objects.filter(y_reserved__gt=0)):
            obj.y_reserved = 0
            await sync_to_async(obj.save)()

        await asyncio.sleep(0)

        ymarket_orders_results = await asyncio.gather(*tasks)
        for i, city in enumerate(ymarket_orders_results):
            for order in city["orders"]:
                for item in order["items"]:
                    try:
                        obj = await Product.objects.aget(
                            y_warehouse=y_whs[i],
                            y_sku=item["offerId"],
                        )
                        obj.y_reserved = item["count"]
                        # logger.warning(f"ya Reserve: {item['offerId']}, {list(warehouses.keys())[i]}, {item['count']}")
                        await sync_to_async(obj.save)()
                    except ObjectDoesNotExist:
                        logger.warning("Reserve: Не найден товар ya", item["offerId"], y_whs[i])

    async def pull_wb_reserved(self):
        wb_orders_results = await wb.pull_new_orders()
        wb_orders_results = await wb.pull_orders_status(wb_orders_results)

        for order in wb_orders_results["orders"]:
            if order["supplierStatus"] == "new":
                for sku in order["skus"]:
                    try:
                        obj = await Product.objects.aget(
                            wb_warehouse=order["warehouseId"],
                            wb_sku=sku,
                        )
                        obj.wb_reserved += 1
                        await sync_to_async(obj.save)()
                    except ObjectDoesNotExist:
                        logger.warning("Reserve: Не найден товар wb", sku)

    async def poll(self):
        await asyncio.gather(
            # self.pull_ozon_reserved(), потому что резерв ставиться из OrderPoller
            self.pull_ymarket_reserved(),
            self.pull_wb_reserved(),
        )
        self.cache.finalize_cycle()


reserve_poller = ReservePoller()
