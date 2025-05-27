from django.contrib.auth.tokens import PasswordResetTokenGenerator, default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from jwt.utils import force_bytes
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import RegistrationSerializer, SetNewPasswordSerializer, ForgotPasswordSerializer
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.conf import settings
from .utils import email_verification_token
from django.core.mail import send_mail
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import get_object_or_404

User = get_user_model()
token_generator = default_token_generator

class RegisterView(generics.CreateAPIView):
    serializer_class = RegistrationSerializer

    def perform_create(self, serializer):
        user = serializer.save()
        # Emailga tasdiqlash linkini yuborish
        token = email_verification_token.make_token(user)
        uid = user.pk
        verify_url = f"http://localhost:8000{reverse('email-verify', kwargs={'uid': uid, 'token': token})}"

        send_mail(
            subject='Emailni tasdiqlash',
            message=f'Emailni tasdiqlash uchun link: {verify_url}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )

class VerifyEmail(generics.GenericAPIView):
    def get(self, request, uid, token):
        user = get_object_or_404(User, pk=uid)
        if email_verification_token.check_token(user, token):
            user.email_verified = True
            user.is_active = True
            user.save()
            return Response({'message': 'Email tasdiqlandi.'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Token noto‘g‘ri yoki muddati o‘tgan.'}, status=status.HTTP_400_BAD_REQUEST)




class ResetPasswordConfirmView(APIView):
    def post(self, request, uid, token):
        serializer = SetNewPasswordSerializer(data={**request.data, 'uid': uid, 'token': token})
        serializer.is_valid(raise_exception=True)

        user = get_object_or_404(User, pk=uid)
        token_generator = PasswordResetTokenGenerator()
        if not token_generator.check_token(user, token):
            return Response({"error": "Token noto'g'ri yoki muddati o'tgan."}, status=400)

        user.set_password(serializer.validated_data['password'])
        user.save()
        return Response({"message": "Parol muvaffaqiyatli yangilandi."})




class ForgotPasswordView(APIView):
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "Bunday email bilan foydalanuvchi topilmadi."},
                            status=status.HTTP_400_BAD_REQUEST)

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = token_generator.make_token(user)

        reset_link = f"http://yourfrontend.com/reset-password/{uid}/{token}/"
        subject = "Parolni tiklash uchun havola"
        message = f"Parolingizni tiklash uchun quyidagi havolani bosing:\n{reset_link}"
        from_email = "no-reply@yourdomain.com"
        recipient_list = [email]

        send_mail(subject, message, from_email, recipient_list)

        return Response({"success": "Tiklash kodi emailga yuborildi."}, status=status.HTTP_200_OK)


class SetNewPasswordView(APIView):
    def post(self, request):
        serializer = SetNewPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        password = serializer.validated_data['password']
        token = serializer.validated_data['token']
        uidb64 = serializer.validated_data['uid']

        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({"error": "Noto‘g‘ri foydalanuvchi yoki token."},
                            status=status.HTTP_400_BAD_REQUEST)

        if not token_generator.check_token(user, token):
            return Response({"error": "Token noto‘g‘ri yoki muddati o'tgan."},
                            status=status.HTTP_400_BAD_REQUEST)

        user.set_password(password)
        user.save()

        return Response({"success": "Parol muvaffaqiyatli yangilandi."}, status=status.HTTP_200_OK)
