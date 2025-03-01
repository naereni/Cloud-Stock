import asyncio

from asgiref.sync import sync_to_async

from api.markets import ozon, wb, ymarket
from api.utils.logger import logger, tglog


async def push_stocks():
    from Cloud_Stock.models import Product

    modified_products = await sync_to_async(list)(Product.objects.filter(is_sync=True, is_modified=True))

    ozon_stocks = []
    ya_stocks = []
    wb_stocks = []

    for product in modified_products:
        # if product.total_stock == 3:
        #     stock_ozon = 2
        #     stock_ymarket = 1
        #     stock_wb = 0
        # elif product.total_stock == 2:
        #     stock_ozon = 1
        #     stock_ymarket = 1
        #     stock_wb = 0
        # elif product.total_stock == 1:
        #     stock_ozon = 0
        #     stock_ymarket = 1
        #     stock_wb = 0
        # else:
        #     stock_ozon = stock_ymarket = stock_wb = product.total_stock


        if product.ozon_sku and product.ozon_warehouse:
            ozon_stocks.append({"product_id": product.ozon_sku, "stock": product.available_stock, "warehouse_id": product.ozon_warehouse})
        # if product.y_sku and product.y_warehouse:
        #     tasks.append(ymarket.update_stock(product.y_sku, product.y_warehouse, stock_ymarket))
        # if product.wb_sku and product.wb_warehouse:
        #     tasks.append(wb.update_stock(product.wb_sku, product.wb_warehouse, stock_wb))

        logger.info(f"Push OYW - | {stock_ozon} | {stock_ymarket} | {stock_wb} | - [{product.city} {product.y_sku}]")
        # await tglog(
        #     f"🔴🔴🔴ОТПРАВКА\n{product.name}\n{product.city}\nprev total_stock: {product.prev_total_stock}\nnew total_stock: {product.total_stock}\nOYW: {stock_ozon}|{stock_ymarket}|{stock_wb}\nHistory \n{"\n".join([" ".join([t["timestamp"],t["user"],str(t["new_stock"])]) for t in product.history])}"
        # )
        product.is_modified = False
        await sync_to_async(product.save)()
    
    if ozon_stocks != []:
        responce = await ozon.push_stocks(ozon_stocks)
    
    
    # responce = await asyncio.gather(*tasks)
    logger.info(f"PUSH OZON RESPONCE - {responce}")
