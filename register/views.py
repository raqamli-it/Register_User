from time import timezone

from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import login, logout
from .serializers import *
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail
import random

class RegisterView(APIView):
    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({"msg": "Tasdiqlash kodingiz emailga yuborildi"}, status=201)

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

class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            request.user.auth_token.delete()
            return Response({"msg": "Tizimdan chiqildi"}, status=status.HTTP_200_OK)
        except:
            return Response({"error": "Token topilmadi"}, status=status.HTTP_400_BAD_REQUEST)

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
        serializer = SetNewPasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            verification = serializer.validated_data['verification_obj']
            new_password = serializer.validated_data['new_password']

            user.set_password(new_password)
            user.save()

            verification.is_used = True
            verification.save()

            return Response({"success": "Parol muvaffaqiyatli o‘zgartirildi."})
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VerifyEmailView(APIView):
    def post(self, request):
        code = request.data.get('code')

        if not code:
            return Response({'error': 'Kod kiritilishi kerak'}, status=400)

        try:
            user = Foydalanuvchi.objects.get(verification_code=code)
        except Foydalanuvchi.DoesNotExist:
            return Response({'error': 'Noto‘g‘ri yoki eskirgan tasdiqlash kodi'}, status=404)

        user.is_active = True
        user.verification_code = None  # kodni tozalaymiz
        user.save()

        return Response({'success': 'Email tasdiqlandi'}, status=200)