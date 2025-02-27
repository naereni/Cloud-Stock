from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from django.views.generic import RedirectView

from api.views import get_logs, pull_ozon_stocks, success_pull, switch_push_stocks
from Cloud_Stock.views import (InfoDeleteView, InfoUpdateView, create, home,
                               login_view, user_stock_update)

urlpatterns = [
    path("", RedirectView.as_view(url="login/")),
    path("login/", login_view, name="login"),
    path("home/", home, name="home"),
    path("create/", create, name="create"),
    path("user_stock_update/", user_stock_update, name="user_stock_update"),
    path("update/<int:pk>/", InfoUpdateView.as_view(), name="update"),
    path("delete/<int:pk>/", InfoDeleteView.as_view(), name="delete"),
    path("pull_ozon_stocks/", pull_ozon_stocks, name="pull_ozon_stocks"),
    path("success_pull/", success_pull, name="success_pull"),
    path("logs/", get_logs, name="logs"),
    path("switch-push-stocks/", switch_push_stocks, name="switch_push_stocks")
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
