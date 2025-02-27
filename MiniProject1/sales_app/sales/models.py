from django.db import models, transaction, IntegrityError
from django.contrib.auth import get_user_model
from products.models import Product
from trading.models import TradeOrder
from rest_framework import serializers
from django.utils import timezone

User = get_user_model()

class Discount(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    discount_type = models.CharField(
        max_length=10,
        choices=[("percentage", "Percentage"), ("fixed", "Fixed Amount")],
    )
    value = models.DecimalField(max_digits=10, decimal_places=2)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    active = models.BooleanField(default=True)

    def apply_discount(self, amount):
        if self.discount_type == "percentage":
            return amount * (1 - self.value / 100)
        return max(amount - self.value, 0)

    def __str__(self):
        return f"{self.name} ({self.value} {self.get_discount_type_display()})"


class Order(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("shipped", "Shipped"),
        ("completed", "Completed"),
        ("canceled", "Canceled"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    discount = models.ForeignKey(Discount, on_delete=models.SET_NULL, null=True, blank=True)

    def calculate_total(self):
        total = sum(item.price * item.quantity for item in self.items.all())

        if self.discount:
            total = self.discount.apply_discount(total)

        self.total_price = total
        self.save(update_fields=["total_price"])

    def __str__(self):
        return f"Order {self.id} - {self.user.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2, editable=False)

    def save(self, *args, **kwargs):
        cheapest_order = TradeOrder.objects.filter(
            product=self.product, order_type="sell", status="pending"
        ).order_by("price", "created_at").first()

        if not cheapest_order:
            raise serializers.ValidationError(f"No available sell orders for {self.product.name}.")

        self.price = cheapest_order.price
        super().save(*args, **kwargs)

        self.order.calculate_total()

    def __str__(self):
        return f"{self.quantity} x {self.product.name} (Order {self.order.id})"


class Invoice(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="invoice")
    invoice_number = models.CharField(max_length=20, unique=True, blank=True)
    issued_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField(null=True, blank=True)
    paid = models.BooleanField(default=False)
    pdf_file = models.FileField(upload_to="invoices/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Invoice {self.invoice_number} for Order {self.order.id}"
