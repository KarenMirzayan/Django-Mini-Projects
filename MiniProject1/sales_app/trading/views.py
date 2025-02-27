from rest_framework import generics, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import TradeOrder, Transaction
from .serializers import TradeOrderSerializer, TransactionSerializer
from .filters import TradeOrderFilter, TransactionFilter
from django.db.models import Q
from .permissions import IsOwnerOrReadOnly
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from django.utils import timezone
from rest_framework import serializers
from rest_framework import permissions

class TradeOrderListView(generics.ListCreateAPIView):
    serializer_class = TradeOrderSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = TradeOrderFilter
    ordering_fields = ["created_at", "price"]

    def get_queryset(self):
        user = self.request.user    
        user_orders = self.request.GET.get("my_orders", None)

        if user_orders:
            return TradeOrder.objects.filter(user=user)

        cache_key = "trade_orders_public"
        cached_data = cache.get(cache_key)

        if cached_data:
            return cached_data

        queryset = TradeOrder.objects.filter(status="pending")
        cache.set(cache_key, queryset, timeout=60 * 15)
        return queryset
    
    def get_permissions(self):
        self.permission_classes = [permissions.AllowAny]
        user_orders = self.request.GET.get("my_orders", None)
        if user_orders:
            self.permission_classes = [permissions.IsAuthenticated]
        return super().get_permissions()

class TradeOrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = TradeOrder.objects.all()
    serializer_class = TradeOrderSerializer
    permission_classes = [IsOwnerOrReadOnly]

    def perform_update(self, serializer):
        if serializer.instance.status in ["executed", "canceled"]:
            raise serializers.ValidationError("Cannot update an executed or canceled order") 
        serializer.save()

    def perform_destroy(self, instance):
        if instance.status in ["executed", "canceled"]:
            raise serializers.ValidationError("Cannot delete an executed or canceled order")
        instance.delete()

            

class TransactionListView(generics.ListAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = TransactionFilter
    ordering_fields = ["timestamp", "price"]

    def get_queryset(self):
        return Transaction.objects.filter(
            Q(buy_order__user=self.request.user) | Q(sell_order__user=self.request.user)
        ).order_by("-timestamp")

class TransactionDetailView(generics.RetrieveAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Transaction.objects.filter(
            Q(buy_order__user=self.request.user) | Q(sell_order__user=self.request.user)
        )