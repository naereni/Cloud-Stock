from asgiref.sync import async_to_sync
from django.core.management.base import BaseCommand

from api.markets import ozon, wb, ymarket
from config.wh import ozon_whs, wb_whs, y_whs


class Command(BaseCommand):
    help = "Load stocks"

    def handle(self, *args, **kwargs):
        from Cloud_Stock.models import Product

        ozon_stocks = ozon.get_stocks(
            list(
                set(
                    [
                        str(sku)
                        for sku in Product.objects.all().values_list("ozon_sku", flat=True)
                        if sku != None and sku != ""
                    ]
                )
            )
        )["result"]
        ozon_stocks_len = len(ozon_stocks)
        for i, item in enumerate(ozon_stocks):
            print(f"Loading stocks: {i}/{ozon_stocks_len}", end="\r")
            try:
                product = Product.objects.get(ozon_sku=item["sku"], ozon_warehouse=item["warehouse_id"])
                if not product.is_complement:
                    product.total_stock = item["present"]
                    product.ozon_reserved = item["reserved"]
                    product.last_user = "First poll from Ozon"
                    product.save()
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f"Error while load stocks for [{item["sku"]}, {item["warehouse_id"]}, {item["present"]}, {item["reserved"]}]: {e}"
                    )
                )

        self.stdout.write(self.style.SUCCESS("Successfully load all products stocks"))
