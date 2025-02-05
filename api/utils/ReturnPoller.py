import asyncio

from asgiref.sync import sync_to_async
from django.core.exceptions import ObjectDoesNotExist

from api.logger import log
from api.markets import ozon, ymarket, wb
from api.utils.CacheManager import CacheManager
from Cloud_Stock.models import Product
from config.wh import y_whs


class ReturnPoller:
    def __init__(self):
        self.cache = CacheManager("Return cache")

    async def save_return_to_db(self, warehouse_id: int, sku: str, quantity: int, service: str):
        cache_key = f"{service}:{warehouse_id}:{sku}"
        if not self.cache.is_in_cache(cache_key):
            try:
                filters = {
                    "ozon_sku": sku if service == "ozon" and hasattr(Product, "ozon_sku") else None,
                    "wb_sku": sku if service == "wb" and hasattr(Product, "wb_sku") else None,
                    "y_sku": sku if service == "ymarket" and hasattr(Product, "y_sku") else None,
                    "ozon_warehouse": (
                        warehouse_id if service == "ozon" and hasattr(Product, "ozon_warehouse") else None
                    ),
                    "wb_warehouse": (
                        warehouse_id if service == "wb" and hasattr(Product, "wb_warehouse") else None
                    ),
                    "y_warehouse": (
                        warehouse_id if service == "ymarket" and hasattr(Product, "y_warehouse") else None
                    ),
                }

                # Удаляем ключи с значением None
                filters = {k: v for k, v in filters.items() if v is not None}

                obj = await Product.objects.aget(**filters)
                obj.stock += quantity
                obj.is_modified = True
                obj.last_user = "RTP"
                await sync_to_async(obj.save)()
                log.info(f"RTP: {obj.name}, new stock: {obj.stock}, SKU: {sku}, Service: {service}")
            except ObjectDoesNotExist:
                log.warning(
                    f"RTP: Product not found for return order: SKU {sku}, Warehouse {warehouse_id}, Service: {service}"
                )
            except Exception as e:
                log.error(f"RTP: Ошибка при сохранении возврата: {str(e)}")

    async def fetch_ozon_returns(self):
        try:
            ozon_returned_orders = await ozon.pull_returned()
            for order in ozon_returned_orders.get("returns", []):
                await self.save_return_to_db(
                    warehouse_id=order["place"]["id"],
                    sku=order["product"]["sku"],
                    quantity=order["product"]["quantity"],
                    service="ozon",
                )
            log.info("RTP: Обработаны возвраты Ozon")
        except Exception as e:
            log.error(f"RTP: Ошибка при получении возвратов Ozon: {str(e)}")

    async def fetch_ymarket_returns(self):
        try:
            tasks = [ymarket.pull_returned_orders(campaign_id) for campaign_id in y_whs]
            ymarket_returned_orders = await asyncio.gather(*tasks, return_exceptions=True)
            for i, city_orders in enumerate(ymarket_returned_orders):
                if isinstance(city_orders, Exception):
                    log.error(
                        f"RTP: Ошибка при получении возвратов Ymarket для кампании {y_whs[i]}: {str(city_orders)}"
                    )
                    continue
                for order in city_orders.get("orders", []):
                    for item in order.get("items", []):
                        await self.save_return_to_db(
                            warehouse_id=y_whs[i],
                            sku=item["offerId"],
                            quantity=item["count"],
                            service="ymarket",
                        )
            log.info("RTP: Обработаны возвраты Ymarket")
        except Exception as e:
            log.error(f"RTP: Ошибка при обработке возвратов Ymarket: {str(e)}")

    async def fetch_wb_returns(self):
        try:
            wb_orders_results = await wb.pull_new_orders()
            wb_orders_results = await wb.pull_orders_status(wb_orders_results)

            for order in wb_orders_results.get("orders", []):
                if order["wbStatus"] == "canceled":
                    for sku in order["skus"]:
                        await self.save_return_to_db(
                            warehouse_id=order["warehouseId"], sku=sku, quantity=1, service="wb"
                        )
            log.info("RTP: Обработаны возвраты Wildberries")
        except Exception as e:
            log.error(f"RTP: Ошибка при обработке возвратов Wildberries: {str(e)}")

    async def poll(self):
        await asyncio.gather(
            self.fetch_ozon_returns(),
            self.fetch_ymarket_returns(),
            self.fetch_wb_returns(),
        )
        self.cache.finalize_cycle()


return_poller = ReturnPoller()
