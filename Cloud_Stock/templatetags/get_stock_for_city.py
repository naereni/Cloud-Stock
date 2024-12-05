# Cloud_Stock/templatetags/get_stock_for_city.py
from django import template

register = template.Library()


@register.filter
def get_stock_for_city(stocks, city_code):
    """Returns the stock for a specific city."""
    return stocks.get(city_code, 0)
