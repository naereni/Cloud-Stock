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
    wb_sku = models.CharField(max_length=100, null=True)

    city = models.CharField(max_length=10, choices=cities)

    y_warehouse = models.IntegerField(null=True)
    ozon_warehouse = models.IntegerField(null=True)
    wb_warehouse = models.IntegerField(null=True)

    stock = models.IntegerField(default=0)
    prev_ozon_stock = models.IntegerField(default=0)
    prev_stock = models.IntegerField(default=0)

    ozon_reserved = models.IntegerField(default=0)
    y_reserved = models.IntegerField(default=0)
    wb_reserved = models.IntegerField(default=0)
    avito_reserved = models.IntegerField(default=0)

    last_user = models.CharField(max_length=100, default="On build")
    last_time = models.CharField(max_length=20)
    is_sync = models.BooleanField(default=False)
    is_modified = models.BooleanField(default=False)
    is_complement = models.BooleanField(default=False)
    history = models.JSONField(default=list)

    def add_to_history(self, user, new_stock):
        timestamp = dateformat.format(timezone.now() + timedelta(hours=3), "d.m.Y H:i:s")
        history_entry = {
            "timestamp": timestamp,
            "user": user,
            "new_stock": new_stock,
        }
        self.history.insert(0, history_entry)
        # logger.info(f"Пользователь {user} изменил остаток товара {self.name} с {self.prev_stock} на {new_stock}")

    def __str__(self):
        return self.name

    def save(self, need_history=None, *args, **kwargs):
        if self.is_complement:
            try:
                complement_obj = Product.objects.get(name=self.name.split(" / ")[0], city=self.city)
                complement_obj.stock += self.stock - self.prev_stock
                complement_obj.is_modified = True
                complement_obj.last_user = "Poller-complement"
                complement_obj.save()
            except ObjectDoesNotExist:
                pass

            try:
                complement_obj = Product.objects.get(name=self.name.split(" / ")[1], city=self.city)
                complement_obj.stock += self.stock - self.prev_stock
                complement_obj.is_modified = True
                complement_obj.last_user = "Poller-complement"
                complement_obj.save()
            except ObjectDoesNotExist:
                pass

        self.prev_stock = self.stock
        self.last_time = dateformat.format(
            timezone.now() + timedelta(hours=3),
            "d.m.Y H:i:s",
        )
        if not need_history:
            self.add_to_history(self.last_user, self.stock)
        super().save(*args, **kwargs)
