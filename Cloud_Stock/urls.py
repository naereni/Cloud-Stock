from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from django.views.generic import RedirectView

from Cloud_Stock.views import *

urlpatterns = [
    path("", RedirectView.as_view(url="login/")),
    path("login/", login_view, name="login"),
    path("home/", home, name="home"),
    path("create/", create, name="create"),
    path("user_stock_update/", user_stock_update, name="user_stock_update"),
    path("update/<int:pk>/", InfoUpdateView.as_view(), name="update"),
    path("delete/<int:pk>/", InfoDeleteView.as_view(), name="delete"),
    path("logs/", logs, name="logs"),
    path("sync-kill-switch/", sync_kill_switch, name="sync_kill_switch"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
