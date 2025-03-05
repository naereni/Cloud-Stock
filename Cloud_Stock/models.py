from datetime import timedelta

from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils import dateformat, timezone

from api.utils.logger import logger
from config.wh import cities


class Product(models.Model):
    name = models.CharField(max_length=100)

    y_sku = models.CharField(max_length=100, null=True)
    ozon_sku = models.CharField(max_length=100, null=True)
    ozon_product_id = models.CharField(max_length=100, null=True)
    wb_sku = models.CharField(max_length=100, null=True)

    city = models.CharField(max_length=10, choices=cities)

    y_warehouse = models.IntegerField(null=True)
    ozon_warehouse = models.IntegerField(null=True)
    wb_warehouse = models.IntegerField(null=True)

    total_stock = models.IntegerField(default=0)
    prev_total_stock = models.IntegerField(default=0)
    available_stock = models.IntegerField(default=0)

    ozon_reserved = models.IntegerField(default=0)
    y_reserved = models.IntegerField(default=0)
    wb_reserved = models.IntegerField(default=0)
    avito_reserved = models.IntegerField(default=0)

    last_user = models.CharField(max_length=100, default="On build")
    is_sync = models.BooleanField(default=False)
    is_modified = models.BooleanField(default=False)
    is_part_of_compliment = models.BooleanField(default=False)
    is_complement = models.BooleanField(default=False)
    history = models.JSONField(default=list)

    def __str__(self):
        return self.name

    def add_to_history(self, user, new_stock):
        timestamp = dateformat.format(timezone.now() + timedelta(hours=3), "d.m.Y H:i:s")
        history_entry = {
            "timestamp": timestamp,
            "user": user,
            "new_stock": new_stock,
        }
        self.history.append(history_entry)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,

            'y_sku': self.y_sku,
            'ozon_sku': self.ozon_sku,
            'ozon_product_id': self.ozon_product_id,
            'wb_sku': self.wb_sku,

            'city': self.city,
            'y_warehouse': self.y_warehouse,
            'ozon_warehouse': self.ozon_warehouse,
            'wb_warehouse': self.wb_warehouse,

            'total_stock': self.total_stock,
            'prev_total_stock': self.prev_total_stock,
            'available_stock': self.available_stock,
            
            'ozon_reserved': self.ozon_reserved,
            'y_reserved': self.y_reserved,
            'wb_reserved': self.wb_reserved,
            'avito_reserved': self.avito_reserved,

            'last_user': self.last_user,
            'is_sync': self.is_sync,
            'is_modified': self.is_modified,
            'is_part_of_compliment': self.is_part_of_compliment,
            'is_complement': self.is_complement
        }

    def save(self, is_secondary_call=False, *args, **kwargs):
        logger.info(f"$$$ SAVE {self.__dict__}")
        stock_diff = self.total_stock - self.prev_total_stock

        self.available_stock = (
            self.total_stock - self.ozon_reserved - self.y_reserved - self.wb_reserved - self.avito_reserved
        )

        if stock_diff != 0:
            self.prev_total_stock = self.total_stock
            logger.info(f"{self.last_user} - [{self.city}, {self.name.strip()}] - {stock_diff}")
            self.add_to_history(self.last_user, self.available_stock)
            self.is_modified = True

        if self.is_complement and not is_secondary_call:
            for subname in self.name.split(" / "):
                try:
                    child = Product.objects.get(name=subname, city=self.city)
                    if stock_diff != 0:
                        child.total_stock += stock_diff
                        child.last_user = self.last_user + "-FromComliment(" + (self.y_sku if self.y_sku is not None else self.name) + ")"
                        child.save(is_secondary_call=self.id)
                except ObjectDoesNotExist:
                    pass

        if self.is_part_of_compliment:
            exclude_comp_id = is_secondary_call if is_secondary_call else self.id
            complements = Product.objects.filter(
                is_complement=True, name__contains=self.name, city=self.city
            ).exclude(id=exclude_comp_id)
            for complement in complements:
                subname1, subname2 = complement.name.split(" / ")
                subname = subname1.strip() if self.name == subname2 else subname2.strip()
                try:
                    second_part_stock = Product.objects.get(name=subname, city=self.city).available_stock
                except Exception as e:
                    logger.error(f"Save comp from child '{subname}' error: {e}")
                    second_part_stock = self.available_stock
                complement.total_stock = min(self.available_stock, second_part_stock)
                complement.last_user = self.last_user + "-FromChild(" + (self.y_sku if self.y_sku is not None else self.name) + ")"
                complement.save(is_secondary_call=True)
        

        super().save(*args, **kwargs)
