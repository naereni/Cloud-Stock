import asyncio
from api.services.Ozon import ozon
from api.services.Ymarket import ymarket
from api.services.WB import wb
from Cloud_Stock.models import Product
import logging

logger = logging.getLogger(__name__)


async def send_stocks():
    modified_products = Product.objects.filter(is_modified=True)

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

        if product.ozon_sku and product.ozon_warehouse:
            tasks.append(ozon.update_stock(product.ozon_sku, product.ozon_warehouse, stock_ozon))
        if product.y_sku and product.y_warehouse:
            tasks.append(ymarket.update_stock(product.y_sku, product.y_warehouse, stock_ymarket))
        if product.wb_sku and product.wb_warehouse:
            tasks.append(wb.update_stock(product.wb_sku, product.wb_warehouse, stock_wb))

    await asyncio.gather(*tasks)
    logger.info("Stocks updated!")
    modified_products.update(is_modified=False)
