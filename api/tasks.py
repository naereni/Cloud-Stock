import asyncio

from celery import shared_task

from api.markets import ozon, wb, ymarket
from api.utils.push_stocks import push_stocks


@shared_task
def process_ozon():
    loop = asyncio.get_event_loop()
    if loop.is_running():
        asyncio.create_task(ozon.poll())
    else:
        loop.run_until_complete(ozon.poll())


@shared_task
def process_ymarket():
    loop = asyncio.get_event_loop()
    if loop.is_running():
        asyncio.create_task(ymarket.poll())
    else:
        loop.run_until_complete(ymarket.poll())


@shared_task
def process_wb():
    loop = asyncio.get_event_loop()
    if loop.is_running():
        asyncio.create_task(wb.poll())
    else:
        loop.run_until_complete(wb.poll())


@shared_task
def pushing_stocks():
    loop = asyncio.get_event_loop()
    if loop.is_running():
        asyncio.create_task(push_stocks())
    else:
        loop.run_until_complete(push_stocks())
