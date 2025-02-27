from django.urls import path
from .views import UserRegistrationView, UserRetrieveUpdateDestroyView, ChangePasswordView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path("register/", UserRegistrationView.as_view(), name="user-register"),
    path("profile/<int:pk>", UserRetrieveUpdateDestroyView.as_view(), name="user-profile"),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
]
