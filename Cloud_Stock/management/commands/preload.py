import csv

from django.core.management.base import BaseCommand

from Cloud_Stock.models import Product
from config.django_config import DJANGO_DEBUG
from config.wh import warehouses


class Command(BaseCommand):
    help = "Load users from a CSV file"

    def add_arguments(self, parser):
        parser.add_argument("csv_file", type=str)

    def handle(self, *args, **kwargs):
        csv_file = kwargs["csv_file"]
        csv_data = []
        with open(csv_file, newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                if "/" in row["Название для заявки"]:
                    csv_data.append(row)
                else:
                    csv_data.insert(0, row)

            for row in csv_data:
                for city in warehouses.keys():
                    kwargs = {}
                    if row["SKU Яндекс"] != "":
                        kwargs["y_sku"] = row["SKU Яндекс"] 
                    if row["SKU Озон"] != "":
                        kwargs["ozon_sku"] = row["SKU Озон"] 
                    if row["ozon_product_id"] != "":
                        kwargs["ozon_product_id"] = row["ozon_product_id"] 
                    if row["SKU WB"] != "":
                        kwargs["wb_sku"] = row["SKU WB"] 
                    Product.objects.create(
                        name=row["Название для заявки"].strip(),
                        is_complement=(True if "/" in row["Название для заявки"] else False),
                        city=city,
                        y_warehouse=warehouses[city]["ymarket"],
                        ozon_warehouse=warehouses[city]["ozon"],
                        wb_warehouse=warehouses[city]["wb"],
                        **kwargs
                    )

                    if "/" in row["Название для заявки"]:
                        p1 = row["Название для заявки"].split("/")[0].strip()
                        p2 = row["Название для заявки"].split("/")[1].strip()
                        Product.objects.filter(name=p1).update(is_part_of_compliment=True)
                        Product.objects.filter(name=p2).update(is_part_of_compliment=True)

        self.stdout.write(self.style.SUCCESS("Successfully imported products"))
