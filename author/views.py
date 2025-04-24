from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.authentication import BasicAuthentication  # TokenAuthentication emas, BasicAuthentication
from rest_framework import status
from django.contrib.auth import authenticate
from .models import User
from rest_framework.authtoken.models import Token

class RegisterView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = [BasicAuthentication]  # Basic Authentication faqat bu yerga

    def post(self, request):
        # Foydalanuvchi Basic Auth yordamida tizimga kirdi
        username = request.data.get("username")
        password = request.data.get("password")
        role = request.data.get("role", "pupil")

        if not username or not password:
            return Response({"error": "Username va password talab qilinadi"}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=username).exists():
            return Response({"error": "Bu username allaqachon mavjud"}, status=status.HTTP_400_BAD_REQUEST)

        # Foydalanuvchini yaratish
        user = User.objects.create_user(username=username, password=password, user_type=role)
        token, _ = Token.objects.get_or_create(user=user)

        return Response({"message": "Muvaffaqiyatli ro‘yxatdan o‘tildi", "token": token.key}, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = [BasicAuthentication]  # Basic Authentication faqat bu yerga

    def post(self, request):
        # Foydalanuvchi Basic Auth yordamida tizimga kirdi
        username = request.data.get("username")
        password = request.data.get("password")

        user = authenticate(request, username=username, password=password)
        if not user:
            return Response({"error": "Noto‘g‘ri username yoki password"}, status=status.HTTP_401_UNAUTHORIZED)

        token, _ = Token.objects.get_or_create(user=user)
        return Response({"message": "Muvaffaqiyatli tizimga kirdingiz", "token": token.key})


class LogoutView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = [BasicAuthentication]  # Basic Authentication faqat bu yerga

    def post(self, request):
        request.user.auth_token.delete()
        return Response({"message": "Tizimdan chiqildi"}, status=status.HTTP_200_OK)
