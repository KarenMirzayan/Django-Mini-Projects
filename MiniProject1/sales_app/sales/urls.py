from django.urls import path
from .views import (
    OrderListCreateView, 
    OrderRetreiveUpdateDestroyView,
    InvoiceListCreateView,
    generate_invoice_pdf,
)

urlpatterns = [
    path("orders/", OrderListCreateView.as_view(), name="order-list-create"),
    path("orders/<int:pk>/", OrderRetreiveUpdateDestroyView.as_view(), name="order-detail"),
    path("invoices/", InvoiceListCreateView.as_view(), name="invoice-list"),
    path("invoices/<int:invoice_id>/pdf/", generate_invoice_pdf, name="invoice-pdf"),
]
