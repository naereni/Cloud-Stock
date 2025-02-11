import asyncio

from celery import shared_task

from api.pollers import order_poller, reserve_poller, return_poller
from api.utils.push_stocks import push_stocks


@shared_task
def polling_orders():
    loop = asyncio.get_event_loop()
    if loop.is_running():
        asyncio.create_task(order_poller.poll())
    else:
        loop.run_until_complete(order_poller.poll())


@shared_task
def polling_reserved():
    loop = asyncio.get_event_loop()
    if loop.is_running():
        asyncio.create_task(reserve_poller.poll())
    else:
        loop.run_until_complete(reserve_poller.poll())


@shared_task
def polling_returned():
    loop = asyncio.get_event_loop()
    if loop.is_running():
        asyncio.create_task(return_poller.poll())
    else:
        loop.run_until_complete(return_poller.poll())


@shared_task
def pushing_stocks():
    loop = asyncio.get_event_loop()
    if loop.is_running():
        asyncio.create_task(push_stocks())
    else:
        loop.run_until_complete(push_stocks())
