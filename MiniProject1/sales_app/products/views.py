from rest_framework import generics, filters
from django_filters.rest_framework import DjangoFilterBackend
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.core.cache import cache
from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated


class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.order_by("name")
    serializer_class = CategorySerializer

    @method_decorator(cache_page(60 * 15, key_prefix="category_list"))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    def get_permissions(self):
        self.permission_classes = [AllowAny]
        if self.request.method == 'POST':
            self.permission_classes = [IsAdminUser]
        return super().get_permissions()


class CategoryRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        self.permission_classes = [AllowAny]
        if self.request.method in ['PUT', 'DELETE', 'PATCH']:
            self.permission_classes = [IsAdminUser]
        return super().get_permissions()



class ProductListCreateView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["category", "tags__name", "price"]
    search_fields = ["name", "description"]
    ordering_fields = ["name", "price", "created_at"]

    @method_decorator(cache_page(60 * 15, key_prefix="product_list"))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    def get_permissions(self):
        self.permission_classes = [AllowAny]
        if self.request.method == 'POST':
            self.permission_classes = [IsAdminUser]
        return super().get_permissions()


class ProductRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_permissions(self):
        self.permission_classes = [AllowAny]
        if self.request.method in ['PUT', 'DELETE', 'PATCH']:
            self.permission_classes = [IsAdminUser]
        return super().get_permissions()
