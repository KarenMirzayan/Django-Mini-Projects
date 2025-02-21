import django_filters
from products.models import *
from rest_framework import filters


class ProductFilter(django_filters.FilterSet):
    class Meta:
        model = Product
        fields = {
            'name': ['iexact', 'icontains'],
            'price': ['exact', 'lt', 'gt', 'range'],
        }
