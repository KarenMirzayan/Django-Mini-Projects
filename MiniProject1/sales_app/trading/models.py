from django.db import models
from django.contrib.auth import get_user_model
from products.models import Product
from django.db import transaction
from django.utils import timezone

User = get_user_model()

class TradeOrder(models.Model):
    ORDER_TYPES = [("buy", "Buy"), ("sell", "Sell")]
    STATUS_CHOICES = [("pending", "Pending"), ("executed", "Executed"), ("canceled", "Canceled")]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="trade_orders")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="trade_orders")
    order_type = models.CharField(max_length=4, choices=ORDER_TYPES)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    executed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user} - {self.order_type} {self.quantity} {self.product.name} @ {self.price}"

class Transaction(models.Model):
    buy_order = models.ForeignKey(TradeOrder, on_delete=models.CASCADE, related_name="buy_transactions")
    sell_order = models.ForeignKey(TradeOrder, on_delete=models.CASCADE, related_name="sell_transactions")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="transactions")
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Trade: {self.quantity} {self.product.name} @ {self.price}"


def match_order(new_order):
    if new_order.order_type == "buy":
        opposite_orders = TradeOrder.objects.filter(
            order_type="sell",
            product=new_order.product,
            status="pending",
            price__lte=new_order.price
        ).order_by("price", "created_at")
    else:
        opposite_orders = TradeOrder.objects.filter(
            order_type="buy",
            product=new_order.product,
            status="pending",
            price__gte=new_order.price
        ).order_by("-price", "created_at")

    with transaction.atomic():
        for opposite_order in opposite_orders:
            if new_order.quantity == 0:
                break

            trade_quantity = min(new_order.quantity, opposite_order.quantity)

            if opposite_order.order_type == "sell":
                trade_price = opposite_order.price
            else:
                trade_price = new_order.price

            Transaction.objects.create(
                buy_order=new_order if new_order.order_type == "buy" else opposite_order,
                sell_order=new_order if new_order.order_type == "sell" else opposite_order,
                product=new_order.product,
                quantity=trade_quantity,
                price=trade_price
            )

            new_order.quantity -= trade_quantity
            opposite_order.quantity -= trade_quantity

            if new_order.quantity == 0:
                new_order.status = "executed"
                new_order.executed_at = timezone.now()
            if opposite_order.quantity == 0:
                opposite_order.status = "executed"
                opposite_order.executed_at = timezone.now()

            new_order.save(update_fields=["quantity", "status", "executed_at"])
            opposite_order.save(update_fields=["quantity", "status", "executed_at"])
