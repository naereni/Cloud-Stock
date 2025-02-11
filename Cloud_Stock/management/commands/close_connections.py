import asyncio

from django.core.management.base import BaseCommand

from api.markets import ozon, wb, ymarket


class Command(BaseCommand):
    async def close(self):
        await ozon.close_session()
        await ymarket.close_session()
        await wb.close_session()

    def handle(self, *args, **kwargs):
        asyncio.run(self.close())
        self.stdout.write(self.style.SUCCESS("Successfully close all aiohttp connections"))
