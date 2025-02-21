from rest_framework import generics
from django.contrib.auth import get_user_model
from .serializers import *
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.exceptions import PermissionDenied
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.hashers import check_password

User = get_user_model()

class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        user = User.objects.get(username=request.data['username'])
        refresh = RefreshToken.for_user(user)
        response.data['token'] = {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }
        return response


class UserRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.request.method == 'DELETE':
            return [IsAdminUser()]
        return [IsAuthenticated()]
    
    def get_object(self):
        obj = super().get_object()
        if self.request.user != obj and not self.request.user.is_staff:
            raise PermissionDenied("You can only update your own profile.")
        return obj


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        serializer = ChangePasswordSerializer(data=request.data)

        if serializer.is_valid():
            old_password = serializer.validated_data["old_password"]
            new_password = serializer.validated_data["new_password"]

            if not check_password(old_password, user.password):
                return Response({"error": "Old password is incorrect"}, status=400)

            user.set_password(new_password)
            user.save()
            return Response({"message": "Password updated successfully"}, status=200)

        return Response(serializer.errors, status=400)