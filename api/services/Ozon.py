from config.api_config import Ozon_config
from datetime import datetime, timedelta
import requests
import json
from api.utils.session_manager import SessionManager


class Ozon:
    def __init__(self) -> None:
        self.headers = {
            "Client-Id": Ozon_config.client_id,
            "Api-Key": Ozon_config.key,
        }

    async def pull_reserved(self):
        session = await SessionManager.get_session()
        url = "https://api-seller.ozon.ru/v3/posting/fbs/list"
        date_to = datetime.now()
        date_from = (date_to - timedelta(minutes=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
        date_to = date_to.strftime("%Y-%m-%dT%H:%M:%SZ")

        request_data = {
            "dir": "ASC",
            "filter": {
                "since": date_from,
                "to": date_to,
                "status": "delivering",
            },
            "limit": 100,
        }

        async with session.post(url, headers=self.headers, json=request_data) as response:
            return await response.json()

    async def pull_returned(self):
        session = await SessionManager.get_session()
        url = "https://api-seller.ozon.ru/v3/returns/company/fbs"
        date_to = datetime.now()
        date_from = (date_to - timedelta(minutes=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
        date_to = date_to.strftime("%Y-%m-%dT%H:%M:%SZ")

        request_data = {
            "dir": "ASC",
            "filter": {
                "since": date_from,
                "to": date_to,
                "status": "returned_to_seller",
            },
            "limit": 100,
        }
        async with session.post(url, headers=self.headers, json=request_data) as response:
            return await response.json()

    async def pull_new_orders(self):
        session = await SessionManager.get_session()
        url = "https://api-seller.ozon.ru/v3/posting/fbs/list"
        date_to = datetime.now()
        date_from = (date_to - timedelta(minutes=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
        date_to = date_to.strftime("%Y-%m-%dT%H:%M:%SZ")

        request_data = {
            "dir": "ASC",
            "filter": {
                "since": date_from,
                "to": date_to,
                "status": "awaiting_deliver",
            },
            "limit": 100,
        }

        async with session.post(url, headers=self.headers, json=request_data) as response:
            return await response.json()

    def pull_new_orders_sync(self):
        url = "https://api-seller.ozon.ru/v3/posting/fbs/list"
        date_to = datetime.now()
        date_from = (date_to - timedelta(minutes=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
        date_to = date_to.strftime("%Y-%m-%dT%H:%M:%SZ")

        request_data = {
            "dir": "ASC",
            "filter": {
                "since": date_from,
                "to": date_to,
                "status": "awaiting_deliver",
            },
            "limit": 100,
        }

        response = requests.post(url, headers=self.headers, json=request_data)
        return response.json()

    async def aget_stocks(self, skus: list):
        session = await SessionManager.get_session()
        url = "https://api-seller.ozon.ru/v1/product/info/stocks-by-warehouse/fbs"
        request_data = {"sku": skus}

        async with session.post(url, headers=self.headers, json=request_data) as response:
            result = await response.json()
            return result["result"]

    def get_stocks(self, skus: list):
        url = "https://api-seller.ozon.ru/v1/product/info/stocks-by-warehouse/fbs"
        request_data = {"sku": skus}

        response = requests.post(url, headers=self.headers, json=request_data).json()
        return response["result"]

    async def get_warehouses_async(self):
        session = await SessionManager.get_session()
        url = "https://api-seller.ozon.ru/v1/warehouse/list"

        async with session.post(url, headers=self.headers) as response:
            result = await response.json()
            houses = [{"warehouse_id": house["warehouse_id"], "name": house["name"]} for house in result["result"]]
            return houses

    def get_warehouses(self):
        url = "https://api-seller.ozon.ru/v1/warehouse/list"
        r = requests.post(url, headers=self.headers).json()
        houses = [{"warehouse_id": house["warehouse_id"], "name": house["name"]} for house in r["result"]]
        return houses

    def check_product_in_warehouse(self, sku, warehouse_id):
        url = "https://api-seller.ozon.ru/v1/product/info/stocks"
        data = {"offer_id": sku, "warehouse_id": warehouse_id}

        response = requests.post(url, headers=self.headers, json=data)
        result = response.json()
        for stock_info in result.get("result", []):
            if stock_info.get("warehouse_id") == warehouse_id:
                return stock_info.get("present", 0) > 0
        return False

    async def test(self, *args, **kwargs):
        return json.loads(
            """{
    "id":572842730,
    "status":"PROCESSING",
    "substatus":"STARTED",
    "creationDate":"25-10-2024 20:46:55",
    "updatedAt":"25-10-2024 20:47:13",
    "currency":"RUR",
    "itemsTotal":19201.0,
    "deliveryTotal":599.0,
    "buyerItemsTotal":19201.0,
    "buyerTotal":19800.0,
    "buyerItemsTotalBeforeDiscount":37757.0,
    "buyerTotalBeforeDiscount":38356.0,
    "paymentType":"PREPAID",
    "paymentMethod":"YANDEX",
    "fake":false,
    "items":[
        {
            "id":731400047,
            "offerId":"Мила_140х200",
            "offerName":"Двуспальная кровать Пора Спать Мила, с подъемным механизмом, спальное место: 140х200см, габариты: 148х208см, цвет: серый",
            "price":19201.0,
            "buyerPrice":19201.0,
            "buyerPriceBeforeDiscount":37757.0,
            "priceBeforeDiscount":37757.0,
            "count":1,
            "vat":"NO_VAT",
            "shopSku":"Мила_140х200",
            "subsidy":1071.0,
            "partnerWarehouseId":"05630967-0ab4-457e-a45a-3dd9fad44016",
            "promos":[
                {
                    "type":"DISCOUNT_BY_PAYMENT_TYPE",
                    "subsidy":59.0
                },
                {
                    "type":"DISCOUNT_BY_PAYMENT_TYPE",
                    "subsidy":196.0
                },
                {
                    "type":"PERCENT_DISCOUNT",
                    "subsidy":816.0
                }
            ],
            "subsidies":[
                {
                    "type":"SUBSIDY",
                    "amount":1071.0
                }
            ]
        }
    ],
    "subsidies":[
        {
            "type":"DELIVERY",
            "amount":300.0
        },
        {
            "type":"SUBSIDY",
            "amount":1071.0
        }
    ],
    "delivery":{
        "type":"DELIVERY",
        "serviceName":"Доставка",
        "price":599.0,
        "deliveryPartnerType":"SHOP",
        "dates":{
            "fromDate":"27-10-2024",
            "toDate":"27-10-2024",
            "fromTime":"00:00:00",
            "toTime":"00:00:00"
        },
        "region":{
            "id":214,
            "name":"Долгопрудный",
            "type":"CITY",
            "parent":{
                "id":120999,
                "name":"Городской округ Долгопрудный",
                "type":"REPUBLIC_AREA",
                "parent":{
                    "id":1,
                    "name":"Москва и Московская область",
                    "type":"REPUBLIC",
                    "parent":{
                        "id":3,
                        "name":"Центральный федеральный округ",
                        "type":"COUNTRY_DISTRICT",
                        "parent":{
                            "id":225,
                            "name":"Россия",
                            "type":"COUNTRY"
                        }
                    }
                }
            }
        },
}"""
        )


ozon = Ozon()
