from api.markets.MetaMarket import Market
from config.api_config import Ymarket_config
from config.django_config import DJANGO_DEBUG
from config.wh import y_whs
import asyncio
from api.utils import CacheManager, asave_product, logger, tglog
from datetime import datetime, timedelta



class Ymarket(Market):
    def __init__(self):
        super().__init__(
            market="Ymarket",
            base_url=(
                "https://api.partner.market.yandex.ru/" if not DJANGO_DEBUG else "http://127.0.0.1:8080/y"
            ),
            headers={
                "Authorization": f"Bearer {Ymarket_config.key}",
                "Content-Type": "application/json",
            },
            max_concurrent_requests=6
        )
        self.business_id = Ymarket_config.business_id
        self.status_map = {
            "PROCESSING": ("YaNew", lambda qty: (qty, qty)),
            "DELIVERED": ("YaComplited", lambda qty: (0, -qty)),
            "CANCELLED": ("YaCancelled", lambda qty: (-qty, -qty)),
            "PICKED": ("YmReject", lambda qty: (-qty, -qty)),

            "USER_UNREACHABLE": ("YaCancelled-USER_UNREACHABLE", lambda qty: (-qty, -qty)),
            "USER_CHANGED_MIND": ("YaCancelled-USER_CHANGED_MIND", lambda qty: (-qty, -qty)),
            "USER_REFUSED_DELIVERY": ("YaCancelled-USER_REFUSED_DELIVERY", lambda qty: (-qty, -qty)),
            "USER_REFUSED_PRODUCT": ("YaCancelled-USER_REFUSED_PRODUCT", lambda qty: (-qty, -qty)),
            "SHOP_FAILED": ("YaCancelled-SHOP_FAILED", lambda qty: (-qty, -qty)),
            "REPLACING_ORDER": ("YaCancelled-REPLACING_ORDER", lambda qty: (-qty, -qty)),
            "DELIVERY_SERVICE_UNDELIVERED": ("YaCancelled-DELIVERY_SERVICE_UNDELIVERED", lambda qty: (-qty, -qty)),
            "USER_WANTS_TO_CHANGE_DELIVERY_DATE": ("YaCancelled-USER_WANTS_TO_CHANGE_DELIVERY_DATE", lambda qty: (-qty, -qty))
        }

    async def poll(self):
        await asyncio.gather(
            self.process_orders(),
            # self.process_returned(),
        )
        self.cache.clean()

    async def process_orders(self, first_time=False):
        endpoint = "v2/campaigns/{0}/orders"
        request_data = {"fromDate": (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")}
        # tasks = [self._aget(endpoint.format(campaign_id, request_data)) for campaign_id in y_whs]
        tasks = [self._aget(endpoint.format("25877039"), request_data)]
        
        responces = await asyncio.gather(*tasks)
        for i, wh in enumerate(responces):
            logger.info(f"\n\n$$$$$$$ YANDEX {wh}")
            for order in wh["orders"]:
                status, operation = self.status_map.get(order.get("status", None), (False, lambda x: 0))
                if status == "YaCancelled":
                    status, operation = self.status_map.get(order.get("substatus", None), (False, lambda x: 0))                    
                if status and not self.cache.check(str(order["id"])+status) and not first_time:
                    logger.info(f"{status} {order}")
                    for item in order["items"]:
                        qty, res = operation(item['count'])
                        await asave_product(
                            service=status,
                            filters={"y_warehouse": y_whs[i], "y_sku": item["offerId"]},
                            quantity=qty,
                            y_reserved=res
                        )

    async def process_returned(self, campaign_id):
        endpoint = "campaigns/{0}/returns"
        request_data = {"fromDate": (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")}
        tasks = [self._aget(endpoint.format(campaign_id, request_data)) for campaign_id in y_whs]
        
        responces = await asyncio.gather(*tasks)   

        for i, wh in enumerate(responces):
            logger.info(f"$$$$$$$ YANDEX {order}")
            for order in wh["returns"]:
                status, operation = self.status_map.get(order.get("shipmentStatus", None), (False, lambda x: 0))
                if status and not self.cache.check(str(order["id"])):
                    logger.info(f"{status} {order}")
                    for item in order["items"]:
                        await asave_product(
                            service=status,
                            filters={
                                "y_warehouse": y_whs[i],
                                "y_sku": item["offerId"],
                            },
                            quantity=-int(item["count"]),
                        )     


    async def pull_stocks(self, campaign_id, skus: list):
        endpoint = f"v2/campaigns/{campaign_id}/offers/stocks"
        request_data = {"offerIds": skus}
        return await self._apost(endpoint, request_data)

    def get_warehouses(self):
        endpoint = f"v2/businesses/{self.business_id}/warehouses"
        r = self._get(endpoint)
        return [
            {"warehouse_id": house["campaignId"], "name": house["name"]}
            for house in r["result"]["warehouses"]
        ]


# async def main():
#     ymarket = Ymarket()
#     r = await ymarket.process_orders("73312497")
#     print("$$$$$$$$$",r)
# import asyncio
# asyncio.run(main())
