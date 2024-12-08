from django.core.management.base import BaseCommand

from api.services.Ozon import ozon
from api.services.WB import wb
from api.services.Ymarket import ymarket
from config.wh import ozon_whs, wb_whs, y_whs


class Command(BaseCommand):
    help = "Load stocks"

    def handle(self, *args, **kwargs):
        from Cloud_Stock.models import Product

        ozon_stocks = ozon.get_stocks(
            list(set([str(sku) for sku in Product.objects.all().values_list("ozon_sku", flat=True) if sku != ""]))
        )
        ozon_stocks_len = len(ozon_stocks)
        for i, item in enumerate(ozon_stocks):
            print(f"Loading stocks: {i}/{ozon_stocks_len}", end="\r")
            try:
                product = Product.objects.get(ozon_sku=item["sku"], ozon_warehouse=item["warehouse_id"])
                product.stock = item["present"]
                product.prev_ozon_stock = item["present"]
                product.ozon_reserved = item["reserved"]
                product.save()
            except:
                pass

        self.stdout.write(self.style.SUCCESS("Successfully load all products stocks"))
