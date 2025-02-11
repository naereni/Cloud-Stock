import asyncio
from typing import Any

from django.core.management.base import BaseCommand

from api.markets import ozon, wb, ymarket
from api.utils.CacheManager import CacheManager
from config.wh import y_whs


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        order_cache = CacheManager("Orders cache")
        return_cache = CacheManager("Return cache")

        async def fetch_delivered_orders():
            tasks = []
            for campaign_id in y_whs:
                tasks.append(ymarket.pull_orders(campaign_id))
            return await asyncio.gather(*tasks)

        delivered_orders_results = asyncio.run(fetch_delivered_orders())
        for delivered_orders in delivered_orders_results:
            for order in delivered_orders.get("orders", []):
                _ = order_cache.check(str(order["id"]))

        self.stdout.write(self.style.SUCCESS("Successfully fill ymarket cache"))
