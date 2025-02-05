from django import forms

from .models import Product


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "name",
            "y_sku",
            "ozon_sku",
            "wb_sku",
            "city",
            "stock",
            "y_reserved",
            "ozon_reserved",
            "wb_reserved",
            "avito_reserved",
            "is_sync",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Название"}),
            "y_sku": forms.TextInput(attrs={"class": "form-control", "placeholder": "ЯМ SKU"}),
            "ozon_sku": forms.TextInput(attrs={"class": "form-control", "placeholder": "Озон SKU"}),
            "wb_sku": forms.TextInput(attrs={"class": "form-control", "placeholder": "ВБ SKU"}),
            "city": forms.Select(attrs={"class": "form-control"}),
            "stock": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "Количество на складе"}
            ),
            "is_sync": forms.CheckboxInput(attrs={"class": "form-check"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["city"].required = True
        self.fields["city"].empty_label = None


class LoginForm(forms.Form):
    username = forms.CharField(max_length=150, required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)


class SearchForm(forms.Form):
    query = forms.CharField(label="Поиск по наименованию", max_length=100)


class StockUpdateForm(forms.Form):
    def __init__(self, *args, **kwargs):
        products = kwargs.pop("products", None)
        super().__init__(*args, **kwargs)

        # Для каждого продукта создаем поле для ввода остатков
        if products:
            for product in products:
                self.fields[f"stock_{product.id}"] = forms.IntegerField(
                    label=f"Остаток на {product.city}",
                    initial=product.stock,
                    required=False,
                    widget=forms.NumberInput(attrs={"class": "form-control"}),
                )
