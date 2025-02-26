import asyncio
from typing import Any

from asgiref.sync import sync_to_async
from django.core.management.base import BaseCommand

from api.markets import ozon, wb, ymarket
from api.utils.CacheManager import CacheManager
from config.wh import y_whs


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        try:

            async def prefill_cache():
                return await asyncio.gather(
                    ozon.process_orders(first_time=True),
                    sync_to_async(ozon.cache.clean)(),
                    ymarket.process_orders(first_time=True),
                    sync_to_async(ymarket.cache.clean)(),
                    wb.process_orders(first_time=True),
                    sync_to_async(wb.cache.clean)(),
                )

            _ = asyncio.run(prefill_cache())

            self.stdout.write(self.style.SUCCESS("Successfully fill ymarket cache"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(e))
