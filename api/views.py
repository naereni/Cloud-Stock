from django.http import JsonResponse
from django.shortcuts import render, redirect
from api.services.Ozon import ozon
from api.services.Ymarket import ymarket
from api.services.WB import wb
from Cloud_Stock.models import Product


def markets_stock_update(row_to_update: dict):
    product = Product.objects.get(name=row_to_update["name"], city=row_to_update["city"])
    product.stock = row_to_update["stock"]
    product.save()


def pull_ozon_stocks(request):
    ozon_stocks = ozon.get_stocks(
        list(set([str(sku) for sku in Product.objects.all().values_list("ozon_sku", flat=True) if sku != ""]))
    )
    for item in ozon_stocks:
        try:
            product = Product.objects.get(ozon_sku=item["sku"], ozon_warehouse=item["warehouse_id"])
            product.stock = item["present"]
            product.ozon_reserved = item["reserved"]
            product.save()
        except:
            pass

    return redirect("success_pull")


def success_pull(request):
    return render(request, "success_pull.html")
