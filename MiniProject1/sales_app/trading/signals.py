from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import TradeOrder


@receiver([post_save, post_delete], sender=TradeOrder)
def invalidate_trade_order_cache(sender, instance, **kwargs):
    cache.delete_pattern('*trade_orders_public*')


