import asyncio
import logging
from api.services.Ozon import ozon
from api.services.Ymarket import ymarket
from api.services.WB import wb
from config.wh import y_whs
from Cloud_Stock.models import Product
from api.utils.CacheManager import CacheManager
from asgiref.sync import sync_to_async
from django.core.exceptions import ObjectDoesNotExist
from api.response_examples import *
from logging.handlers import RotatingFileHandler
import pathlib
from datetime import datetime

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

handler = RotatingFileHandler(
    str(pathlib.Path(__file__).parent.parent.parent / "logs/OrderPoller.log"),
    mode="a",
    encoding="UTF-8",
    maxBytes=1024 * 1024 * 64,
    backupCount=3,
)
handler.setFormatter(formatter)
logger.addHandler(handler)


class OrderPoller:
    def __init__(self):
        self.cache = CacheManager("Orders cache")

    async def poll_ozon_orders(self):
        q = (
            list(await sync_to_async(
                lambda: list(Product.objects.filter(ozon_sku__isnull=False)
                .exclude(ozon_sku="")
                .values_list("ozon_sku", flat=True)
                .distinct())
            )())
        )
        await sync_to_async(print)(q)
        ozon_stocks = await ozon.aget_stocks(q)
        logger.warning(f"Дата изменения запаса")
        for item in ozon_stocks:
            try:
                product = await Product.objects.aget(ozon_sku=item["sku"], ozon_warehouse=item["warehouse_id"])
                stock_change = item["present"] - product.prev_ozon_stock
                product.stock = max(0, product.stock + stock_change)
                product.prev_ozon_stock = item["present"]
                product.ozon_reserved = item["reserved"]
                if stock_change != 0:
                    product.is_modified = True
                    product.last_user = "Stock poller ozon"
                logger.info(f"Poll_order: {product.name} - {stock_change}")
                await sync_to_async(product.save)()
            except ObjectDoesNotExist:
                logger.warning(
                    f"Poll_order: Не найден товар ozon SKU:{item['sku']}, Warehouse:{item['warehouse_id']}, Item:{item['present']}"
                )

    async def poll_ymarket_orders(self):
        tasks = []
        for campaign_id in y_whs:
            tasks.append(ymarket.pull_new_orders(campaign_id))

        ymarket_orders_results = await asyncio.gather(*tasks)

        for i, city in enumerate(ymarket_orders_results):
            for order in city["orders"]:
                if not self.cache.is_in_cache(str(order["id"])):
                    for item in order["items"]:
                        try:
                            obj = await Product.objects.aget(
                                y_warehouse=y_whs[i],
                                y_sku=item["offerId"],
                            )
                            obj.stock = max(0, obj.stock - item["count"])
                            obj.is_modified = True
                            obj.last_user = "Order poller ya"
                            await sync_to_async(obj.save)()
                        except ObjectDoesNotExist:
                            logger.warning(f"Poll_order: Не найден товар ya {item['offerId']}")

    async def poll_wb_orders(self):
        wb_orders_results = await wb.pull_new_orders()
        wb_orders_results = await wb.pull_orders_status(wb_orders_results)

        for order in wb_orders_results["orders"]:
            if not self.cache.is_in_cache(str(order["id"])) and order["wbStatus"] == "sold":
                for sku in order["skus"]:
                    try:
                        obj = await Product.objects.aget(
                            wb_warehouse=order["warehouseId"],
                            wb_sku=sku,
                        )
                        obj.stock = max(0, obj.stock - 1)
                        obj.is_modified = True
                        obj.last_user = "Order poller wb"
                        await sync_to_async(obj.save)()
                    except ObjectDoesNotExist:
                        logger.warning(f"Poll_order: Не найден товар wb {sku}")

    async def poll(self):
        await asyncio.gather(
            self.poll_ozon_orders(),
            self.poll_ymarket_orders(),
            self.poll_wb_orders(),
        )
        self.cache.finalize_cycle()


order_poller = OrderPoller()
