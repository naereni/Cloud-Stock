from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import DeleteView, UpdateView

from api.views import markets_stock_update
from Cloud_Stock.decorators import login_required
from Cloud_Stock.forms import LoginForm, ProductForm, SearchForm
from Cloud_Stock.models import Product


@login_required
def handler404(request, *args, **kwargs):
    return redirect("login")


@login_required
def home(request):
    form = SearchForm()
    query = None
    selected_city = request.GET.get("city", "all")

    # Получение списка продуктов
    products = Product.objects.all()

    # Фильтрация по запросу
    if "query" in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data["query"]
            products = products.filter(name__icontains=query)

    # Список всех городов
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
        # Отображение таблицы для всех складов
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
                "name": product.name,
                "total_stock": product.total_stock
                - (product.ozon_reserved + product.y_reserved + product.wb_reserved + product.avito_reserved),
                "y_reserved": product.y_reserved,
                "ozon_reserved": product.ozon_reserved,
                "wb_reserved": product.wb_reserved,
                "avito_reserved": product.avito_reserved,
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
                    product.total_stock = int(value)
                    markets_stock_update(product.__dict__)
                except Product.DoesNotExist:
                    print(f"Product with id {product_id} does not exist")
            elif key.startswith("avito_"):
                product_id = key.split("_")[-1]
                try:
                    product = Product.objects.get(id=product_id)
                    product.avito_reserved = int(value)
                    product.save()
                except Product.DoesNotExist:
                    print(f"Product with id {product_id} does not exist")
        city = request.POST.get("city", "all")
        return redirect(f"{reverse('home')}?city={city}")
    return HttpResponse("Invalid request method", status=405)
