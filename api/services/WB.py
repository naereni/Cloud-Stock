from config.api_config import WB_config
import requests
from api.utils.session_manager import SessionManager


class WB:
    def __init__(self) -> None:
        self.headers = {
            "Authorization": WB_config.key,
            "Content-Type": "application/json",
        }

    async def pull_orders_status(self, orders_data: dict):
        session = await SessionManager.get_session()
        order_ids = [order["id"] for order in orders_data["orders"]]
        url = f"https://marketplace-api.wildberries.ru/api/v3/orders/status"
        request_data = {"orders": order_ids}
        async with session.post(url, headers=self.headers, json=request_data) as response:
            if "application/json" in response.headers.get("Content-Type", ""):
                result = await response.json()
                if "orders" in result:
                    status_map = {order["id"]: order for order in result["orders"]}

                    for order in orders_data["orders"]:
                        order_id = order["id"]
                        if order_id in status_map:
                            order["supplierStatus"] = status_map[order_id].get("supplierStatus", "")
                            order["wbStatus"] = status_map[order_id].get("wbStatus", "")

                return orders_data

            else:
                text = await response.text()
                print(f"Unexpected content type: {text}")
                return None

    async def pull_returned_orders(self, orders_data: dict):
        session = await SessionManager.get_session()
        url = "https://marketplace-api.wildberries.ru/api/v3/orders/status"
        order_ids = [order["id"] for order in orders_data["orders"]]
        request_data = {"orders": order_ids}
        async with session.post(url, headers=self.headers, json=request_data) as response:
            if "application/json" in response.headers.get("Content-Type", ""):
                result = await response.json()
                if "orders" in result:
                    status_map = {order["id"]: order for order in result["orders"]}

                    for order in orders_data["orders"]:
                        order_id = order["id"]
                        if order_id in status_map:
                            order["supplierStatus"] = status_map[order_id].get("supplierStatus", "")
                            order["wbStatus"] = status_map[order_id].get("wbStatus", "canceled")
                return orders_data
            else:
                text = await response.text()
                print(f"Unexpected content type: {text}")
                return None

    async def pull_new_orders(self):
        session = await SessionManager.get_session()
        url = "https://marketplace-api.wildberries.ru/api/v3/orders/new"
        async with session.get(url, headers=self.headers) as response:
            if "application/json" in response.headers.get("Content-Type", ""):
                return await response.json()
            else:
                text = await response.text()
                print(f"Unexpected content type: {text}")
                return None

    async def pull_stocks(self, warehouse_id, skus: list):
        session = await SessionManager.get_session()
        url = f"https://marketplace-api.wildberries.ru/api/v3/stocks/{warehouse_id}"
        request_data = {"skus": skus}
        async with session.post(url, headers=self.headers, json=request_data) as response:
            if "application/json" in response.headers.get("Content-Type", ""):
                result = await response.json()
                return result
            else:
                text = await response.text()
                print(f"Unexpected content type: {text}")
                return None

    def get_warehouses(self):
        url = "https://suppliers-api.wildberries.ru/api/v3/warehouses"
        response = requests.get(url, headers=self.headers)
        if "application/json" in response.headers.get("Content-Type", ""):
            warehouses = response.json()
            houses = []
            for house in warehouses:
                houses.append(
                    {
                        "warehouse_id": house["officeId"],
                        "name": house["name"],
                    }
                )
            return houses
        else:
            print(f"Unexpected content type: {response.text}")
            return []

    def check_product_in_warehouse(self, sku, warehouse_id):
        url = f"https://suppliers-api.wildberries.ru/api/v1/stocks"
        params = {"search": sku}
        response = requests.get(url, headers=self.headers, params=params).json()
        for stock_info in response.get("stocks", []):
            if stock_info.get("warehouseId") == warehouse_id:
                return stock_info.get("quantity", 0) > 0
        return False


wb = WB()
