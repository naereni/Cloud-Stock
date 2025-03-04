import asyncio

from asgiref.sync import sync_to_async

from api.markets import ozon, wb, ymarket
from api.utils.logger import logger, tglog


async def push_stocks():
    from Cloud_Stock.models import Product

    modified_products = await sync_to_async(list)(Product.objects.filter(is_sync=True, is_modified=True))

    ozon_stocks = []
    y_stocks = {}
    wb_stocks = {}

    for product in modified_products:
        if product.available_stock == 3:
            ozon_stock = 2
            y_stock = 1
            wb_stock = 0
        elif product.available_stock == 2:
            ozon_stock = 1
            y_stock = 1
            wb_stock = 0
        elif product.available_stock == 1:
            ozon_stock = 0
            y_stock = 1
            wb_stock = 0
        else:
            ozon_stock = y_stock = wb_stock = product.available_stock

        if product.ozon_sku and product.ozon_warehouse:
            ozon_stocks.append({"product_id": product.ozon_product_id, "stock": ozon_stock, "warehouse_id": product.ozon_warehouse})
        if product.y_sku and product.y_warehouse:
            y_stocks.setdefault(str(product.y_warehouse), [])
            y_stocks[str(product.y_warehouse)].append({"sku": product.y_sku, "items": [{"count": y_stock}]})
        if product.wb_sku and product.wb_warehouse:
            wb_stocks.setdefault(str(product.wb_warehouse), [])
            wb_stocks[str(product.wb_warehouse)].append({"sku": str(product.wb_sku), "amount": wb_stock})

        logger.info(f"Push OYW - {ozon_stock} | {y_stock} | {wb_stock} - [{product.city} / {product.y_sku}]")
        product.is_modified = False
        await sync_to_async(product.save)()

    tasks = []
    if ozon_stocks != []:
        tasks.append(ozon.push_stocks(ozon_stocks))
    if y_stocks != {}:
        tasks.append(ymarket.push_stocks(y_stocks))
    if wb_stocks != {}:
        tasks.append(wb.push_stocks(wb_stocks))

    if tasks != []:
        responces = await asyncio.gather(*tasks)
        for response in responces:
            logger.info("Responce from push -", response)
