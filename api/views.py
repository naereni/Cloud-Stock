import os

from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render

from api.markets import ozon, wb, ymarket
from Cloud_Stock.models import Product
from Cloud_Stock.settings import BASE_DIR
from config.django_config import LOG_FILE
from celery.app.control import Control
from Cloud_Stock.celery import app
from api.utils import logger

LOG_FILE_PATH = os.path.join(BASE_DIR, LOG_FILE)


def markets_stock_update(row_to_update: dict):
    product = Product.objects.get(name=row_to_update["name"], city=row_to_update["city"])
    product.total_stock = row_to_update["total_stock"]
    product.save()


def pull_ozon_stocks(request):
    ozon_stocks = ozon.get_stocks(
        list(set([str(sku) for sku in Product.objects.all().values_list("ozon_sku", flat=True) if sku != ""]))
    )
    for item in ozon_stocks:
        try:
            product = Product.objects.get(ozon_sku=item["sku"], ozon_warehouse=item["warehouse_id"])
            product.total_stock = item["present"]
            product.ozon_reserved = item["reserved"]
            product.save()
        except:
            pass

    return redirect("success_pull")


def success_pull(request):
    return render(request, "success_pull.html")


def get_logs(request):
    if not os.path.exists(LOG_FILE_PATH):
        return JsonResponse({"error": "Log file not found"}, status=404)

    try:
        with open(LOG_FILE_PATH, "r", encoding="utf-8") as log_file:
            logs = log_file.readlines()
        return HttpResponse("".join(logs[-1000:][::-1]), content_type="text/plain")
    except Exception as e:
        return JsonResponse({"error": "Failed to read logs - {e}"}, status=500)


def switch_push_stocks(request):
    if request.method == 'POST':
        control = Control(app)
        task_name = 'api.tasks.pushing_stocks'
        
        # Get current state of the task
        inspect = app.control.inspect()
        active_tasks = inspect.active() or {}
        is_task_running = any(task.get('name') == task_name for tasks in active_tasks.values() for task in tasks)
        
        if is_task_running:
            # Revoke the task
            app.control.revoke(task_name, terminate=True)
            is_enabled = False
            logger.warning("Push stocks disabled")
        else:
            # Enable the task
            app.control.enable_events()
            is_enabled = True
            logger.warning("Push stocks enabled")
        
        return JsonResponse({'is_enabled': is_enabled})
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)
