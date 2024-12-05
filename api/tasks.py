import asyncio
from celery import shared_task
from django.urls import reverse
from django.test import Client
from api.utils.push_stocks import send_stocks
from api.utils.OrderPoller import order_poller
from api.utils.ReservePoller import reserve_poller
from api.utils.ReturnPoller import return_poller
from api.views import pull_ozon_stocks


@shared_task
def polling_orders():
    print("start_polling")
    loop = asyncio.get_event_loop()
    if loop.is_running():
        asyncio.create_task(order_poller.poll())
    else:
        loop.run_until_complete(order_poller.poll())


@shared_task
def polling_reserved():
    print("start_polling_reserv")
    loop = asyncio.get_event_loop()
    if loop.is_running():
        asyncio.create_task(reserve_poller.poll())
    else:
        loop.run_until_complete(reserve_poller.poll())


@shared_task
def polling_returned():
    print("start_polling_returned")
    loop = asyncio.get_event_loop()
    if loop.is_running():
        asyncio.create_task(return_poller.poll())
    else:
        loop.run_until_complete(return_poller.poll())


@shared_task
def send_stocks():
    print("send_stocks")
    loop = asyncio.get_event_loop()
    if loop.is_running():
        asyncio.create_task(send_stocks())
    else:
        loop.run_until_complete(send_stocks())
