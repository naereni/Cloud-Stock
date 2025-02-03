from typing import Any
from django.core.management.base import BaseCommand
from api.utils.CacheManager import CacheManager
from api.markets.Ymarket import ymarket
import asyncio
from config.wh import y_whs

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        cache = CacheManager("Orders cache")
        
        async def fetch_delivered_orders():
            tasks = []
            for campaign_id in y_whs: 
                tasks.append(ymarket.pull_new_orders(campaign_id))
            return await asyncio.gather(*tasks)
            
        delivered_orders_results = asyncio.run(fetch_delivered_orders())
        for delivered_orders in delivered_orders_results:
            for order in delivered_orders.get("orders", []):
                _ = cache.is_in_cache(str(order["id"])) 

        self.stdout.write(self.style.SUCCESS("Successfully fill ymarket cache"))