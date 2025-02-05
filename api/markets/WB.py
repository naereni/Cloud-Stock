from api.logger import log
from api.markets.Market import Market
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
        response = await self._apost(endpoint, request_data)

        if "orders" in response:
            status_map = {order["id"]: order for order in response["orders"]}

            for order in orders_data["orders"]:
                order_id = order["id"]
                if order_id in status_map:
                    order["supplierStatus"] = status_map[order_id].get("supplierStatus", "")
                    order["wbStatus"] = status_map[order_id].get("wbStatus", "")
        else:
            log.market_api(f"ERROR while get wb statuses, Unexpected content type: {response.text}")

        return orders_data

    # TODO нарушена логика с ReturnPoller.fetch_wb_returns
    async def pull_returned_orders(self, orders_data: dict):
        endpoint = "v3/orders/status"

        order_ids = [order["id"] for order in orders_data["orders"]]
        request_data = {"orders": order_ids}
        response = await self._apost(endpoint, request_data)
        if "orders" in response:
            status_map = {order["id"]: order for order in response["orders"]}

            for order in orders_data["orders"]:
                order_id = order["id"]
                if order_id in status_map:
                    order["supplierStatus"] = status_map[order_id].get("supplierStatus", "")
                    order["wbStatus"] = status_map[order_id].get("wbStatus", "canceled")
        else:
            log.market_api(f"ERROR while get wb returned, Unexpected content type: {response.text}")

        return orders_data

    async def pull_new_orders(self):
        endpoint = "v3/orders/new"

        response = await self._aget(endpoint)
        if "application/json" in response.headers.get("Content-Type", ""):
            # TODO возвращать только при 200 или в любом случае? как тогда оно должно выглядеть
            return response
        else:
            log.market_api(f"ERROR while get wb new orders, Unexpected content type: {response.text}")

    async def pull_stocks(self, warehouse_id, skus: list):
        endpoint = f"v3/stocks/{warehouse_id}"

        request_data = {"skus": skus}
        response = await self._apost(endpoint, request_data)
        if "application/json" in response.headers.get("Content-Type", ""):
            return response
        else:
            log.market_api(f"ERROR while get wb stocks, Unexpected content type: {response.text}")

    def get_warehouses(self):
        endpoint = "https://suppliers-api.wildberries.ru/api/v3/warehouses"

        response = self._get(endpoint)
        if "application/json" in response.headers.get("Content-Type", ""):
            houses = []
            for house in response:
                houses.append(
                    {
                        "warehouse_id": house["officeId"],
                        "name": house["name"],
                    }
                )
            return houses
        else:
            log.market_api(f"ERROR while get wb new whs, Unexpected content type: {response.text}")
