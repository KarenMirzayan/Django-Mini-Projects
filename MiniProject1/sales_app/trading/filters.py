import django_filters
from .models import TradeOrder, Transaction

class TradeOrderFilter(django_filters.FilterSet):
    status = django_filters.ChoiceFilter(choices=TradeOrder.STATUS_CHOICES)
    order_type = django_filters.ChoiceFilter(choices=TradeOrder.ORDER_TYPES)
    product = django_filters.NumberFilter(field_name="product__id")

    class Meta:
        model = TradeOrder
        fields = ["status", "order_type", "product"]

class TransactionFilter(django_filters.FilterSet):
    product = django_filters.NumberFilter(field_name="product__id")
    min_price = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    max_price = django_filters.NumberFilter(field_name="price", lookup_expr="lte")

    class Meta:
        model = Transaction
        fields = ["product", "min_price", "max_price"]
