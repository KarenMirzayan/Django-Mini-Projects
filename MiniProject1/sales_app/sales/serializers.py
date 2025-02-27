from rest_framework import serializers
from django.db import transaction
from .models import Order, OrderItem, Invoice, Discount
from products.models import Product
from trading.models import TradeOrder
from django.db import models


class DiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Discount
        fields = ["id", "name", "code", "discount_type", "value", "valid_from", "valid_to", "active"]


class OrderItemSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = ["id", "product", "quantity", "price"]

    def validate(self, data):
        product = data["product"]
        quantity = data["quantity"]

        cheapest_order = TradeOrder.objects.filter(
            product=product, order_type="sell", status="pending"
        ).order_by("price", "created_at").first()

        if not cheapest_order:
            raise serializers.ValidationError(f"{product.name} is out of stock.")

        if cheapest_order.quantity < quantity:
            raise serializers.ValidationError(
                f"Not enough stock for {product.name} (available: {cheapest_order.quantity})"
            )

        return data


class OrderSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    items = OrderItemSerializer(many=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    discount = DiscountSerializer(read_only=True)
    discount_id = serializers.PrimaryKeyRelatedField(
        queryset=Discount.objects.all(), source="discount", write_only=True, required=False
    )

    class Meta:
        model = Order
        fields = ["id", "user", "status", "items", "total_price", "discount", "discount_id", "created_at"]

    def create_invoice(self, order):
        """Creates an invoice for the given order."""
        invoice = Invoice.objects.create(order=order)
        invoice.invoice_number = f"INV-{invoice.id:06d}"
        invoice.save()
        return invoice

    def fulfill_order(self, product, quantity_needed):
        """Attempts to fulfill the order by buying out the cheapest available trade orders."""
        total_price = 0
        items = []

        trade_orders = TradeOrder.objects.filter(
            product=product, order_type="sell", status="pending"
        ).order_by("price", "created_at")

        for trade_order in trade_orders:
            if quantity_needed <= 0:
                break

            buy_quantity = min(quantity_needed, trade_order.quantity)

            trade_order.quantity -= buy_quantity
            if trade_order.quantity == 0:
                trade_order.status = "completed"
            trade_order.save()

            total_price += trade_order.price * buy_quantity

            items.append(OrderItem(product=product, quantity=buy_quantity, price=trade_order.price))

            quantity_needed -= buy_quantity

        if quantity_needed > 0:
            raise serializers.ValidationError(f"Not enough stock for {product.name}.")

        return items, total_price

    def create(self, validated_data):
        items_data = validated_data.pop("items")
        discount = validated_data.pop("discount", None)
        total_price = 0

        with transaction.atomic():
            order = Order.objects.create(**validated_data)

            for item_data in items_data:
                product = item_data["product"]
                quantity = item_data["quantity"]

                order_items, price = self.fulfill_order(product, quantity)
                total_price += price

                for order_item in order_items:
                    order_item.order = order
                    order_item.save()

            if discount:
                total_price = discount.apply_discount(total_price)
                order.discount = discount

            order.total_price = total_price
            order.status = "completed"
            order.save()

            self.create_invoice(order)

        return order

    def update(self, instance, validated_data):
        items_data = validated_data.pop("items", None)
        discount = validated_data.pop("discount", None)

        with transaction.atomic():
            instance.status = validated_data.get("status", instance.status)

            if discount:
                instance.discount = discount

            instance.items.all().delete()
            total_price = 0

            if items_data:
                for item_data in items_data:
                    product = item_data["product"]
                    quantity = item_data["quantity"]

                    order_items, price = self.fulfill_order(product, quantity)
                    total_price += price

                    for order_item in order_items:
                        order_item.order = instance
                        order_item.save()

            if discount:
                total_price = discount.apply_discount(total_price)

            instance.total_price = total_price
            instance.status = "completed"
            instance.save()

            if not hasattr(instance, "invoice"):
                self.create_invoice(instance)

        return instance



class InvoiceSerializer(serializers.ModelSerializer):
    order = OrderSerializer(read_only=True)
    order_id = serializers.PrimaryKeyRelatedField(queryset=Order.objects.all())

    class Meta:
        model = Invoice
        fields = ["id", "order", "order_id", "invoice_number", "issued_at", "pdf_file"]
