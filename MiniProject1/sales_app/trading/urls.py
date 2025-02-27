from django.urls import path
from .views import (
    TradeOrderListView,
    TradeOrderDetailView,
    TransactionListView,
    TransactionDetailView,
)

urlpatterns = [
    path("trade-orders/", TradeOrderListView.as_view(), name="trade-order-list"),
    path("trade-orders/<int:pk>/", TradeOrderDetailView.as_view(), name="trade-order-detail"),

    path("transactions/", TransactionListView.as_view(), name="transaction-list"),
    path("transactions/<int:pk>/", TransactionDetailView.as_view(), name="transaction-detail"),
]
