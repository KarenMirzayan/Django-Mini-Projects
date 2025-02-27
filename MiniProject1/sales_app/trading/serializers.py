from rest_framework import serializers
from .models import TradeOrder, Transaction
from products.models import Product
from django.db import transaction
from .models import match_order

class TradeOrderSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = TradeOrder
        fields = ["id", "user", "product", "order_type", "quantity", "price", "status", "created_at", "executed_at"]
        read_only_fields = ["status", "created_at", "executed_at"]

    def create(self, validated_data):
        with transaction.atomic():
            new_order = TradeOrder.objects.create(**validated_data)
            match_order(new_order)
        return new_order

class TransactionSerializer(serializers.ModelSerializer):
    buy_order = serializers.PrimaryKeyRelatedField(queryset=TradeOrder.objects.all())
    sell_order = serializers.PrimaryKeyRelatedField(queryset=TradeOrder.objects.all())
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())

    class Meta:
        model = Transaction
        fields = ["id", "buy_order", "sell_order", "product", "quantity", "price", "timestamp"]
