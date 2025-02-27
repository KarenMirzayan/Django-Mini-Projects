from rest_framework import generics
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from .models import Order, Invoice
from .serializers import OrderSerializer, InvoiceSerializer
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from rest_framework.decorators import api_view, permission_classes
from .tasks import send_order_confirmation_email


class OrderListCreateView(generics.ListCreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)
    
    # def perform_create(self, serializer):
    #     order = serializer.save()
    #     send_order_confirmation_email.delay(order.id, order.user.email)



class OrderRetreiveUpdateDestroyView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def perform_update(self, serializer):
        order = self.get_object()
        if order.status in ["completed", "canceled"]:
            raise PermissionDenied("You cannot edit a completed or canceled order.")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.status in ["completed", "canceled"]:
            raise PermissionDenied("You cannot delete a completed or canceled order.")
        instance.delete()


class InvoiceListCreateView(generics.ListCreateAPIView):
    serializer_class = InvoiceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Invoice.objects.filter(order__user=self.request.user)
    
    def perform_create(self, serializer):
        order = serializer.validated_data["order_id"]
        if order.user != self.request.user:
            raise PermissionDenied("You do not have permission to generate an invoice for this order.")
        serializer.save(order=order)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def generate_invoice_pdf(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id, order__user=request.user)
    order = invoice.order
    
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="invoice_{invoice.invoice_number}.pdf"'

    # Create a PDF document
    p = canvas.Canvas(response, pagesize=letter)
    width, height = letter

    # Invoice Header
    p.setFont("Helvetica-Bold", 16)
    p.drawString(200, height - 50, "INVOICE")
    
    p.setFont("Helvetica", 12)
    p.drawString(50, height - 80, f"Invoice Number: {invoice.invoice_number}")
    p.drawString(50, height - 100, f"Date Issued: {invoice.issued_at.strftime('%Y-%m-%d')}")

    # Order Details
    p.drawString(50, height - 160, f"Order ID: {order.id}")
    p.drawString(50, height - 180, f"Customer: {order.user.username}")
    p.drawString(50, height - 200, f"Status: {order.status}")

    # Table Header
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, height - 240, "Product")
    p.drawString(300, height - 240, "Quantity")
    p.drawString(400, height - 240, "Price")
    p.drawString(500, height - 240, "Total")

    # Table Content
    y_position = height - 260
    p.setFont("Helvetica", 12)
    subtotal = 0
    for item in order.items.all():
        item_total = item.quantity * item.price
        subtotal += item_total
        p.drawString(50, y_position, item.product.name)
        p.drawString(300, y_position, str(item.quantity))
        p.drawString(400, y_position, f"{item.price:.2f}")
        p.drawString(500, y_position, f"{item_total:.2f}")
        y_position -= 20

    # Subtotal
    y_position -= 20
    p.setFont("Helvetica-Bold", 12)
    p.drawString(400, y_position, "Subtotal:")
    p.drawString(500, y_position, f"{subtotal:.2f}")

    # Discount (if applied)
    if order.discount:
        discount_amount = subtotal - order.total_price
        y_position -= 20
        p.setFont("Helvetica", 12)
        p.drawString(400, y_position, f"Discount ({order.discount.name}):")
        p.drawString(500, y_position, f"-{discount_amount:.2f}")

    # Total Price
    y_position -= 20
    p.setFont("Helvetica-Bold", 12)
    p.drawString(400, y_position, "Total Price:")
    p.drawString(500, y_position, f"{order.total_price:.2f}")

    p.showPage()
    p.save()

    return response

