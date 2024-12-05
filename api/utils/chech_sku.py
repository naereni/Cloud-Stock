import asyncio
from api.services.Ozon import ozon, Ozon
from api.services.Ymarket import ymarket, Ymarket
from api.services.WB import wb
from config.wh import ozon_whs, y_whs, wb_whs
from Cloud_Stock.models import Product


def check_sku(self, sku, warehouse_id):
    error_skus = []

    # Проверка на Ozon
    if self.ozon_sku and self.ozon_warehouse:
        if not ozon.check_product_in_warehouse(self.ozon_sku, self.ozon_warehouse):
            error_skus.append({"marketplace": "ozon", "sku": self.ozon_sku})
    else:
        error_skus.append({"marketplace": "ozon", "sku": "SKU or warehouse not provided"})

    # Проверка на Yandex Market
    if self.y_sku and self.y_warehouse:
        if not ymarket.check_product_in_warehouse(self.y_sku, self.y_warehouse):
            error_skus.append({"marketplace": "ymarket", "sku": self.y_sku})
    else:
        error_skus.append({"marketplace": "ymarket", "sku": "SKU or warehouse not provided"})

    # Проверка на Wildberries
    if self.wb_sku and self.wb_warehouse:
        if not wb.check_product_in_warehouse(self.wb_sku, self.wb_warehouse):
            error_skus.append({"marketplace": "wildberries", "sku": self.wb_sku})
    else:
        error_skus.append({"marketplace": "wildberries", "sku": "SKU or warehouse not provided"})

    if not error_skus:
        return {"result": True}
    else:
        return {"result": "error", "error_skus": error_skus}
