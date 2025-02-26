from asgiref.sync import sync_to_async
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction

from api.utils.logger import logger


def format_filters(filters: dict) -> str:
    return ", ".join([f"{key}: {value}" for key, value in filters.items()])


async def asave_product(service: str, filters: dict, quantity, **kwargs):
    """
    - order ts-qty reserve+qty
    - complited reserve-qty
    - cancelled ts+qty reserve-qty

    - returned ts+qty reserv-qty
    """

    from Cloud_Stock.models import Product

    ozon_reserved = kwargs.get("ozon_reserved", 0)
    y_reserved = kwargs.get("y_reserved", 0)
    wb_reserved = kwargs.get("wb_reserved", 0)

    try:

        def update_product():
            with transaction.atomic():
                product = Product.objects.select_for_update().get(**filters)

                product.last_user = service

                if (product.total_stock - quantity) < 0:
                    logger.critical(
                        f"{service} - [{format_filters(filters)}] - TRY TO SET QTY == {product.total_stock - quantity}"
                    )

                # product.total_stock = max(0, product.total_stock - quantity)
                product.total_stock -= quantity

                product.ozon_reserved += ozon_reserved
                product.y_reserved += y_reserved
                product.wb_reserved += wb_reserved

                logger.info(f"{service} - [{format_filters(filters)}] - {quantity}")
                product.save()

        await sync_to_async(update_product)()

    except ObjectDoesNotExist:
        logger.warning(f"{service} - [{format_filters(filters)}] - ObjectDoesNotExist")
    except Exception as e:
        logger.error(f"{service} - Error while save: {e}")
