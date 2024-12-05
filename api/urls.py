from django.urls import path
from api.views import *

urlpatterns = [
    path("pull_ozon_stocks/", pull_ozon_stocks, name="pull_ozon_stocks"),
    path("success_pull/", success_pull, name="success_pull"),
]
