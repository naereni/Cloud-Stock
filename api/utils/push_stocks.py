import asyncio

from asgiref.sync import sync_to_async

from api.markets.Ozon import ozon
from api.markets.WB import wb
from api.markets.Ymarket import ymarket
from api.utils.logger import logger
from api.utils.tglogger import tglog
from Cloud_Stock.models import Product


async def push_stocks():
    modified_products = await sync_to_async(list)(Product.objects.filter(is_sync=True, is_modified=True))

    tasks = []
    for product in modified_products:
        if product.stock == 3:
            stock_ozon = 2
            stock_ymarket = 1
            stock_wb = 0
        elif product.stock == 2:
            stock_ozon = 1
            stock_ymarket = 1
            stock_wb = 0
        elif product.stock == 1:
            stock_ozon = 0
            stock_ymarket = 1
            stock_wb = 0
        else:
            stock_ozon = stock_ymarket = stock_wb = product.stock

        # TODO проверить в сервисах
        # if product.ozon_sku and product.ozon_warehouse:
        #     tasks.append(ozon.update_stock(product.ozon_sku, product.ozon_warehouse, stock_ozon))
        # if product.y_sku and product.y_warehouse:
        #     tasks.append(ymarket.update_stock(product.y_sku, product.y_warehouse, stock_ymarket))
        # if product.wb_sku and product.wb_warehouse:
        #     tasks.append(wb.update_stock(product.wb_sku, product.wb_warehouse, stock_wb))

        logger.info(f"Push OYW: {product.name}: {stock_ozon} | {stock_ymarket} | {stock_wb}")
        await tglog(
            f"🔴🔴🔴ОТПРАВКА\n{product.name}\n{product.city}\nprev stock: {product.prev_stock}\nnew stock: {product.stock}\nOYW: {stock_ozon}|{stock_ymarket}|{stock_wb}\nHistory \n{"\n".join([" ".join([t["timestamp"],t["user"],str(t["new_stock"])]) for t in product.history])}"
        )
        product.is_modified = False
        await sync_to_async(product.save)()
    # await asyncio.gather(*tasks)
    logger.info("Stocks updated!")
