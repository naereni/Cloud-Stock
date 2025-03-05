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
            "available_stock",
            "y_reserved",
            "ozon_reserved",
            "wb_reserved",
            "is_sync",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Название"}),
            "y_sku": forms.TextInput(attrs={"class": "form-control", "placeholder": "ЯМ SKU"}),
            "ozon_sku": forms.TextInput(attrs={"class": "form-control", "placeholder": "Озон SKU"}),
            "wb_sku": forms.TextInput(attrs={"class": "form-control", "placeholder": "ВБ SKU"}),
            "city": forms.Select(attrs={"class": "form-control"}),
            "available_stock": forms.NumberInput(
                attrs={
                    "class": "form-control", 
                    "placeholder": "Количество на складе",
                    "min": "0",
                }
            ),
            "is_sync": forms.CheckboxInput(attrs={"class": "form-check"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["city"].required = True
        self.fields["y_sku"].required = False
        self.fields["ozon_sku"].required = False
        self.fields["wb_sku"].required = False


class LoginForm(forms.Form):
    username = forms.CharField(max_length=150, required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)


class SearchForm(forms.Form):
    query = forms.CharField(label="Поиск по наименованию", max_length=100)
