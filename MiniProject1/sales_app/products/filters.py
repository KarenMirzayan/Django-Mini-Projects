import django_filters
from django.db.models import Min
from trading.models import TradeOrder  # Import TradeOrder model
from .models import Product

class ProductFilter(django_filters.FilterSet):
    price = django_filters.NumberFilter(method='filter_by_price')
    price__lt = django_filters.NumberFilter(field_name='price', lookup_expr='lt', method='filter_by_price')
    price__gt = django_filters.NumberFilter(field_name='price', lookup_expr='gt', method='filter_by_price')
    price__range = django_filters.NumericRangeFilter(field_name='price', method='filter_by_price_range')
    tags = django_filters.CharFilter(method='filter_by_tags')

    class Meta:
        model = Product
        fields = {
            'name': ['iexact', 'icontains'],
            'category': ['exact'],
        }

    def filter_by_price(self, queryset, name, value):
        filtered_products = []
        for product in queryset:
            cheapest_order = TradeOrder.objects.filter(
                product=product, order_type="sell", status="pending"
            ).aggregate(min_price=Min("price"))["min_price"]
            
            if cheapest_order is not None and cheapest_order == value:
                filtered_products.append(product.id)

        return queryset.filter(id__in=filtered_products)

    def filter_by_price_range(self, queryset, name, value):
        filtered_products = []
        for product in queryset:
            cheapest_order = TradeOrder.objects.filter(
                product=product, order_type="sell", status="pending"
            ).aggregate(min_price=Min("price"))["min_price"]
            
            if cheapest_order is not None and value[0] <= cheapest_order <= value[1]:
                filtered_products.append(product.id)

        return queryset.filter(id__in=filtered_products)
    
    def filter_by_tags(self, queryset, name, value):
        """
        Custom filter method to filter products by tag name.
        """
        return queryset.filter(tags__name__icontains=value)
