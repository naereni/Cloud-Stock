from asgiref.sync import sync_to_async
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction

from api.utils.logger import logger

async def zero_out_reserved():
    from Cloud_Stock.models import Product
    await sync_to_async(Product.objects.update)(ozon_reserved=0, y_reserved=0, wb_reserved=0)


def format_filters(filters: dict) -> str:
    return ", ".join([f"{key}: {value}" for key, value in filters.items()])


async def asave_product(service: str, filters: dict, quantity):
    """
    Асинхронное обновление записи Product с логгированием.

    Аргументы:
    service (str): Код поллера и рынка, например:
                    - "ORO" – Order Poller для Ozon,
                    - "REY" – Reserve Poller для Yandex (Ymarket),
                    - "RTW" – Return Poller для Wildberries.
    filters (dict): Словарь фильтров для выборки товара (например, {"sku": "12345", "ozon_warehouse": 1})

    Пример использования:

    await save_product_update(
        service="ORO",
        filters={"sku": "1770441663", "ozon_warehouse": 23904191646000},
        quantity=5
    )
    """
    from Cloud_Stock.models import Product
    poller_mapping = {"OR": "Order Poller", "RE": "Reserve Poller", "RT": "Return Poller"}
    market_mapping = {"O": "Ozon", "Y": "Yandex", "W": "WB"}

    try:
        poller_code = service[:2]  # "OR", "RE" или "RT"
        market_code = service[-1]  # "O", "Y" или "W"
        poller_name = poller_mapping.get(poller_code, "Unknown Poller")
        market_name = market_mapping.get(market_code, "Unknown Market")
        last_user = f"{poller_name} {market_name}"
    except Exception as e:
        logger.error(f"Invalid service code '{service}': {e}")

    try:
        def update_product():
            with transaction.atomic():
                product = Product.objects.select_for_update().get(**filters)

                if poller_code == "OR":
                    if (product.stock - quantity) < 0:
                        logger.critical(f"{service} - [{format_filters(filters)}] - TRY TO SET QTY < 0")
                    product.stock = max(0, product.stock - quantity)
                    logger.info(f"{service} - [{format_filters(filters)}] - {quantity}")

                elif poller_code == "RE":
                    if market_code == "O":
                        product.ozon_reserved += quantity
                    elif market_code == "Y":
                        product.y_reserved += quantity
                    elif market_code == "W":
                        product.wb_reserved += quantity
                    logger.debug(f"{service} - done")

                elif poller_code == "RT":
                    product.stock += quantity
                    logger.info(f"{service} - [{format_filters(filters)}] - {quantity}")

                if poller_code != "RE":
                    product.is_modified = True
                    product.last_user = last_user

                product.save()

        await sync_to_async(update_product)()

    except ObjectDoesNotExist:
        logger.warning(f"{service} - [{format_filters(filters)}] - ObjectDoesNotExist")
    except Exception as e:
        logger.error(f"{service} - Error while save: {e}")
