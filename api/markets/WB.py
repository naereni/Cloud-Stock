from api.markets.MetaMarket import Market
from api.utils.logger import logger
from config.api_config import WB_config
from config.django_config import DJANGO_DEBUG


class WB(Market):
    def __init__(self) -> None:
        super().__init__(
            base_url=(
                "https://marketplace-api.wildberries.ru/api/"
                if not DJANGO_DEBUG
                else "http://127.0.0.1:8080/wb"
            ),
            headers={
                "Authorization": WB_config.key,
                "Content-Type": "application/json",
            },
        )

    async def pull_orders_status(self, orders_data: dict):
        endpoint = "v3/orders/status"
        request_data = {"orders": [order["id"] for order in orders_data["orders"]]}
        if request_data["orders"] == []:
            return orders_data
        response = await self._apost(endpoint, request_data)

        try:
            status_map = {order["id"]: order for order in response["orders"]}

            for order in orders_data["orders"]:
                order_id = order["id"]
                if order_id in status_map:
                    order["supplierStatus"] = status_map[order_id].get("supplierStatus", "")
                    order["wbStatus"] = status_map[order_id].get("wbStatus", "")
            return orders_data
        
        except Exception as e:
            logger.warning(f"Packet loss, endpoint={endpoint}, Exception={e}")
            return orders_data


    async def pull_orders(self):
        endpoint = "v3/orders/new"

        return await self._aget(endpoint)

    async def pull_stocks(self, warehouse_id, skus: list):
        endpoint = f"v3/stocks/{warehouse_id}"

        request_data = {"skus": skus}
        return await self._apost(endpoint, request_data)

    def get_warehouses(self):
        endpoint = "https://suppliers-api.wildberries.ru/api/v3/warehouses"

        response = self._get(endpoint)
        try:
            houses = []
            for house in response:
                houses.append(
                    {
                        "warehouse_id": house["officeId"],
                        "name": house["name"],
                    }
                )
            return houses
        except Exception as e:
            logger.warning(f"ERROR while get wb new whs, Unexpected content type: {response.text}")
