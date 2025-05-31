# register/views.py
from time import timezone

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import login, logout
from .models import Foydalanuvchi, ResetCode, VerificationCode
from .serializers import *
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail
import random

class RegisterView(APIView):
    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({"msg": "Foydalanuvchi muvaffaqiyatli ro'yxatdan o'tdi"}, status=201)

class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request, user)
        refresh = RefreshToken.for_user(user)
        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        })

class LogoutView(APIView):
    def post(self, request):
        logout(request)
        return Response({"msg": "Tizimdan chiqildi"}, status=200)

class ForgotPasswordView(APIView):
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']

        try:
            user = Foydalanuvchi.objects.get(email=email)
        except Foydalanuvchi.DoesNotExist:
            return Response({"error": "Bunday foydalanuvchi yo‘q"}, status=400)

        code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        ResetCode.objects.create(user=user, code=code)

        send_mail(
            subject="Tasdiqlash kodi",
            message=f"Sizning parolni tiklash kodingiz: {code}",
            from_email="noreply@example.com",
            recipient_list=[email],
        )

        return Response({"msg": "Emailga tasdiqlash kodi yuborildi"})

class VerifyCodeView(APIView):
    def post(self, request):
        code = request.data.get("code")
        try:
            reset = ResetCode.objects.get(code=code)
            if reset.is_expired():
                return Response({"error": "Kodning muddati tugagan"}, status=400)
            return Response({"msg": "Kod tasdiqlandi", "user_id": reset.user.id})
        except ResetCode.DoesNotExist:
            return Response({"error": "Noto‘g‘ri kod"}, status=400)

class SetNewPasswordView(APIView):
    def post(self, request):
        code = request.data.get("code")
        password = request.data.get("password")
        password_confirm = request.data.get("password_confirm")

        if not all([code, password, password_confirm]):
            return Response({"error": "Barcha maydonlar to'ldirilishi kerak."}, status=400)

        if password != password_confirm:
            return Response({"error": "Parollar mos emas."}, status=400)

        try:
            code_obj = VerificationCode.objects.get(code=code, is_used=False)
        except VerificationCode.DoesNotExist:
            return Response({"error": "Kod noto‘g‘ri yoki foydalanilgan."}, status=400)

        if code_obj.expires_at < timezone.now():
            return Response({"error": "Kod muddati tugagan."}, status=400)

        user = code_obj.user
        user.set_password(password)
        user.save()

        code_obj.is_used = True
        code_obj.save()

        return Response({"success": "Parol muvaffaqiyatli o‘zgartirildi."})
