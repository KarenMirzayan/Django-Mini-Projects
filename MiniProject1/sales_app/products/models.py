from django.db import models
from taggit.managers import TaggableManager
from django.apps import apps

class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey("Category", on_delete=models.CASCADE, related_name="products")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    tags = TaggableManager()

    def __str__(self):
        return self.name
    
    @property
    def price(self):
        TradeOrder = apps.get_model("trading", "TradeOrder")
        cheapest_order = TradeOrder.objects.filter(
            product=self, order_type="sell", status="pending"
        ).aggregate(min_price=models.Min("price"))["min_price"]
        
        return cheapest_order if cheapest_order is not None else 0
    
class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="product_images/")

    def __str__(self):
        return f"Image for {self.product.name}"
