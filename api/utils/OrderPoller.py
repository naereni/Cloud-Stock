import asyncio

from asgiref.sync import sync_to_async
from django.core.exceptions import ObjectDoesNotExist

from api.logger import log, tglog
from api.markets import ozon, ymarket, wb
from api.utils.CacheManager import CacheManager
from Cloud_Stock.models import Product
from config.wh import y_whs


class OrderPoller:
    def __init__(self):
        self.cache = CacheManager("Orders cache")

    async def poll_ozon_orders(self):
        ozon_orders_results = await ozon.pull_orders()
        for posting in ozon_orders_results["result"]["postings"]:
            if not self.cache.is_in_cache(str(posting["order_id"])):
                for item in posting["products"]:
                    try:
                        product = await Product.objects.aget(
                            ozon_warehouse=posting["delivery_method"]["warehouse_id"],
                            ozon_sku=item["sku"],
                        )
                        product.stock = max(0, product.stock - item["quantity"])
                        product.is_modified = True
                        product.last_user = "Order poller ozon"
                        log.debug(f"ORPO: Change {product.name} - {product.prev_stock}->{product.stock}")
                        await sync_to_async(product.save)()
                    except ObjectDoesNotExist:
                        log.warning(f"Poll_order: Не найден товар ozon {item['sku']}")

    async def poll_ozon_stocks(self):
        q = list(
            await sync_to_async(
                lambda: list(
                    Product.objects.filter(ozon_sku__isnull=False)
                    .exclude(ozon_sku="")
                    .values_list("ozon_sku", flat=True)
                    .distinct()
                )
            )()
        )
        ozon_stocks = await ozon.aget_stocks(q)
        log.info("ORP: Ozon stocks+reserved")
        diff_count = 0
        reserved_count = 0
        for item in ozon_stocks:
            try:
                product = await Product.objects.aget(
                    ozon_sku=item["sku"], ozon_warehouse=item["warehouse_id"]
                )
                stock_change = item["present"] - product.prev_ozon_stock
                if item["reserved"] != 0:
                    product.ozon_reserved = item["reserved"]
                    reserved_count += 1
                    await sync_to_async(product.save)(need_history=False)
                if stock_change != 0:
                    product.stock = max(0, product.stock + stock_change)
                    product.prev_ozon_stock = item["present"]
                    product.is_modified = True
                    product.last_user = "ORPO"
                    diff_count += 1
                    log.debug(f"ORPO: Change {product.name} - {product.prev_stock}->{product.stock}")
                    if product.name == "Кровать Мила V32 160х200":
                        await tglog(
                            f"🔵ПОЛУЧЕНИЕ\n{product.city}\nprev stock: {product.prev_stock}\nnew stock: {product.stock}\nRES OYW: {product.ozon_reserved}|{product.y_reserved}|{product.wb_reserved}\nHistory \n{"\n".join(["-".join([t["timestamp"][11:],t["user"],str(t["new_stock"])]) for t in product.history])}"
                        )
                    await sync_to_async(product.save)()
            except ObjectDoesNotExist:
                if item["warehouse_id"] != 1020000632461000:
                    log.warning(
                        f"ORP: Не найден товар ozon SKU:{item['sku']}, Warehouse:{item['warehouse_id']}, Item:{item['present']}"
                    )
        log.info(f"ORP: Ozon diff count: {diff_count}, reserved count: {reserved_count}")

    async def poll_ymarket_orders(self):
        tasks = []
        for campaign_id in y_whs:
            tasks.append(ymarket.pull_orders(campaign_id))

        ymarket_orders_results = await asyncio.gather(*tasks)
        log.info(
            f"ORP: Ymarket orders, orders={sum([len(city['orders']) for city in ymarket_orders_results])}"
        )
        diff_count = 0
        for i, city in enumerate(ymarket_orders_results):
            for order in city["orders"]:
                if not self.cache.is_in_cache(str(order["id"])):
                    for item in order["items"]:
                        try:
                            product = await Product.objects.aget(
                                y_warehouse=y_whs[i],
                                y_sku=item["offerId"],
                            )
                            product.stock = max(0, product.stock - item["count"])
                            product.is_modified = True
                            product.last_user = "ORPY"
                            await sync_to_async(product.save)()
                            diff_count += 1

                            log.debug(
                                f"ORPY: Change {product.name} - {product.prev_stock}->{product.stock}"
                            )
                            if product.name == "Кровать Мила V32 160х200":
                                await tglog(
                                    f"🟡ПОЛУЧЕНИЕ\n{product.city}\nprev stock: {product.prev_stock}\nnew stock: {product.stock}\nRES OYW: {product.ozon_reserved}|{product.y_reserved}|{product.wb_reserved}\nHistory \n{"\n".join(["-".join([t["timestamp"][11:],t["user"],str(t["new_stock"])]) for t in product.history])}"
                                )

                        except ObjectDoesNotExist:
                            log.warning(f"ORP: Не найден товар ya {item['offerId']}")
        log.info(f"ORP: Ymarket diff count: {diff_count}")

    async def poll_wb_orders(self):
        wb_orders_results = await wb.pull_new_orders()
        wb_orders_results = await wb.pull_orders_status(wb_orders_results)
        log.info(f"ORP: Wb orders, orders-{len(wb_orders_results['orders'])}")
        diff_count = 0
        for order in wb_orders_results["orders"]:
            if not self.cache.is_in_cache(str(order["id"])) and order["wbStatus"] == "sold":
                for sku in order["skus"]:
                    try:
                        product = await Product.objects.aget(
                            wb_warehouse=order["warehouseId"],
                            wb_sku=sku,
                        )
                        product.stock = max(0, product.stock - 1)
                        product.is_modified = True
                        product.last_user = "ORPW"
                        await sync_to_async(product.save)()
                        log.debug(f"ORPW: Change {product.name} - {product.prev_stock}->{product.stock}")
                        if product.name == "Кровать Мила V32 160х200":
                            await tglog(
                                f"🟣ПОЛУЧЕНИЕ\n{product.city}\nprev stock: {product.prev_stock}\nnew stock: {product.stock}\nRES OYW: {product.ozon_reserved}|{product.y_reserved}|{product.wb_reserved}\nHistory \n{"\n".join(["-".join([t["timestamp"][11:],t["user"],str(t["new_stock"])]) for t in product.history])}"
                            )

                        diff_count += 1
                    except ObjectDoesNotExist:
                        log.warning(f"ORP: Не найден товар wb {sku}")
        log.info(f"ORP: Wb diff count: {diff_count}")

    async def poll(self):
        await asyncio.gather(
            self.poll_ozon_orders(),
            # self.poll_ymarket_orders(),
            # self.poll_wb_orders(),
        )
        self.cache.finalize_cycle()


order_poller = OrderPoller()
