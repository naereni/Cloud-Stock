from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.views.generic import RedirectView
from api.views import pull_ozon_stocks, success_pull
from Cloud_Stock.views import (
    home,
    create,
    InfoUpdateView,
    InfoDeleteView,
    login_view,
    user_stock_update,
)

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
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)