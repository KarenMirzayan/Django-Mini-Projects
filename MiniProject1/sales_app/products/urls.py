from django.urls import path, include
from . import views

urlpatterns = [
    path('products/', views.ProductListCreateView.as_view(), name='product_list'),
    path('products/<int:pk>/', views.ProductRetrieveUpdateDestroyView.as_view(), name='product_detail'),
    path('categories/', views.CategoryListCreateView.as_view(), name='category_list'),
    path('categories/<int:pk>/', views.CategoryRetrieveUpdateDestroyView.as_view(), name='category_detail'),
]
