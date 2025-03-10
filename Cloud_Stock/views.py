import os
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import DeleteView, UpdateView

from Cloud_Stock.decorators import login_required
from Cloud_Stock.forms import LoginForm, ProductForm, SearchForm
from Cloud_Stock.models import Product

from config.django_config import LOG_FILE
from api.utils import logger

@login_required
def handler404(request, *args, **kwargs):
    return redirect("login")


@login_required
def home(request):
    form = SearchForm()
    query = None
    selected_city = request.GET.get("city", "all")
    products = Product.objects.all()

    if "query" in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data["query"]
            products = products.filter(name__icontains=query)

    city_list = [
        ("spb", "СПБ"),
        ("msk", "МСК"),
        ("samara", "Самара"),
        ("kazan", "Казань"),
        ("krasnodar", "Краснодар"),
        ("nn", "Нижний Новгород"),
        ("ekb", "Екатеринбург"),
        ("rnd", "Ростов"),
        ("nsk", "НСК"),
    ]

    # Подготовка данных для отображения остатков
    if selected_city == "all":
        product_stock = {}
        for product in products:
            if product.name not in product_stock:
                product_stock[product.name] = {}
            product_stock[product.name][product.city] = product.total_stock
            product_stock[product.name]["pk"] = product.pk  # Добавляем pk продукта
    else:
        # Отображение таблицы для конкретного города
        products = products.filter(city=selected_city)
        product_stock = [
            {
                "pk": product.pk,
                "name": product.y_sku,
                "available_stock": product.available_stock,
                "avito_reserved": product.avito_reserved,
                "y_reserved": product.y_reserved,
                "ozon_reserved": product.ozon_reserved,
                "wb_reserved": product.wb_reserved,
                "city": dict(city_list).get(product.city),
            }
            for product in products
        ]

    return render(
        request,
        "home.html",
        {
            "form": form,
            "cities": city_list,
            "product_stock": product_stock,
            "selected_city": selected_city,
        },
    )


class InfoUpdateView(UpdateView):
    model = Product
    template_name = "update.html"
    form_class = ProductForm

    def form_valid(self, form):
        product = form.save(commit=False)
        product.last_user = self.request.user.username
        product.total_stock += product.available_stock - product.total_stock + product.avito_reserved
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["city"] = self.request.GET.get("city", "all")
        context["history"] = self.object.history
        return context

    def get_success_url(self):
        city = self.request.GET.get("city", "all")
        return reverse("home") + f"?city={city}"


class InfoDeleteView(DeleteView):
    model = Product
    success_url = reverse_lazy("home")
    template_name = "confirm_delete.html"


@login_required
def create(request):
    error = ""
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("home")
        else:
            logger.error(form.errors)  
            error = "Проблемы с вводом данных"

    form = ProductForm()
    data = {"form": form, "error": error}
    return render(request, "create.html", data)


def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(request, username=username, password=password)

            if user is not None:
                request.session["username"] = username
                login(request, user)
                return redirect("home")
            else:
                messages.error(request, "Invalid username or password")
    else:
        form = LoginForm()
        return render(request, "login.html", {"form": form})


@login_required
def user_stock_update(request):
    if request.method == "POST":
        for key, value in request.POST.items():
            if key.startswith("stocks_"):
                product_id = key.split("_")[-1]
                try:
                    product = Product.objects.get(id=product_id)
                    stock_diff = int(value) - product.available_stock

                    if stock_diff != 0:
                        product.last_user = "USER"
                        product.total_stock += stock_diff
                        product.save(exclude_id=product.id)

                except Product.DoesNotExist:
                    logger.error(f"Product with id {product_id} does not exist")

            elif key.startswith("avito_"):
                product_id = key.split("_")[-1]
                try:
                    product = Product.objects.get(id=product_id)
                    new_value = int(value)
                    old_value = product.avito_reserved

                    if new_value != old_value:
                        product.last_user = "USER"
                        product.add_to_history("Avito", new_value)
                        logger.info(f"Avito - [{product.city}, {product.name.strip()}] - {new_value}")

                        delta = new_value - old_value
                        if delta < 0:
                            product.total_stock += delta

                        product.avito_reserved = new_value
                        product.save()

                except Product.DoesNotExist:
                    logger.error(f"Product with id {product_id} does not exist")

        city = request.POST.get("city", "all")

        return redirect(f"{reverse('home')}?city={city}")
    return HttpResponse("Invalid request method", status=405)

def logs(request):
    try:
        if not os.path.exists(LOG_FILE):
            return JsonResponse({"error": "Log file not found"}, status=404)
    except Exception as e:
        logger.error("Test error", e)

    try:
        with open(LOG_FILE, "r", encoding="UTF-8") as log_file:
            logs = log_file.readlines()
        return HttpResponse("".join(logs[-1000:][::-1]), content_type="text/plain; charset=UTF-8")
    except Exception as e:
        logger.error(f"Failed to read logs - {e}")
        return JsonResponse({"error": "Failed to read logs - {e}"}, status=500)


@login_required
def sync_kill_switch(request):
    if request.method == "POST":
        control = Control(app)  # Здесь предполагается, что Control - это объект для управления Celery
        task_name = "api.tasks.pushing_stocks"

        try:
            turn_on = request.POST.get("turnOn")  # Получаем 'turnOn' с фронтенда
            if turn_on is None:
                return JsonResponse({"error": "Missing 'turnOn' parameter"}, status=400)

            turn_on = turn_on.lower() == "true"  # Преобразуем строку в булево значение

            if turn_on:
                app.control.enable_events()
                is_enabled = True
                logger.warning("Push stocks enabled")
            else:
                inspect = app.control.inspect()
                active_tasks = inspect.active() or {}
                # Поиск активной задачи по имени
                task_ids = [
                    task.get("id")
                    for tasks in active_tasks.values()
                    for task in tasks
                    if task.get("name") == task_name
                ]
                for task_id in task_ids:
                    app.control.revoke(task_id, terminate=True)  # Завершаем задачу по ID
                is_enabled = False
                logger.warning("Push stocks disabled")

            return JsonResponse({"is_enabled": is_enabled})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)