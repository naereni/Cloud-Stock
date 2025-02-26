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

    def save(self, history=True, *args, **kwargs):
        if self.is_complement:
            for subsku in self.name.split(" / "):
                try:
                    complement_obj = Product.objects.get(name=subsku, city=self.city)
                    if complement_obj.prev_total_stock != complement_obj.total_stock:
                        complement_obj.prev_total_stock = complement_obj.total_stock
                        complement_obj.is_modified = True
                    complement_obj.last_user = "Comliment"
                    complement_obj.save()
                except ObjectDoesNotExist:
                    pass

        if self.prev_total_stock != self.total_stock:
            self.prev_total_stock = self.total_stock
            self.is_modified = True

        self.available_stock = (
            self.total_stock - self.ozon_reserved - self.y_reserved - self.wb_reserved - self.avito_reserved
        )

        if history:
            self.add_to_history(self.last_user, self.total_stock)

        super().save(*args, **kwargs)
