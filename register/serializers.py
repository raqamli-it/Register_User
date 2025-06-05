from rest_framework import serializers
from .models import Foydalanuvchi, ResetCode  # TasdiqlashKodni o'rniga VerificationCode
from django.contrib.auth import authenticate
import re
from django.utils.crypto import get_random_string
from django.utils import timezone
from datetime import timedelta

from .utils import generate_verification_code, send_verification_email


class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = Foydalanuvchi
        fields = ['email', 'username', 'password', 'password2']

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError("Parollar mos emas.")
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        return Foydalanuvchi.objects.create_user(**validated_data)

    def create(self, validated_data):
        validated_data.pop('password2')
        code = generate_verification_code()
        user = Foydalanuvchi.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password'],
            verification_code=code,
            is_active=False
        )
        send_verification_email(user.email, code)
        return user

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, attrs):
        user = authenticate(email=attrs['email'], password=attrs['password'])
        if not user:
            raise serializers.ValidationError("Email yoki parol noto‘g‘ri.")
        attrs['user'] = user
        return attrs


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate(self, attrs):
        email = attrs.get('email')
        try:
            user = Foydalanuvchi.objects.get(email=email)
        except Foydalanuvchi.DoesNotExist:
            raise serializers.ValidationError("Bunday foydalanuvchi yo‘q.")


        code = get_random_string(length=6, allowed_chars='0123456789')
        ResetCode.objects.create(
            user=user,
            code=code,
            expires_at=timezone.now() + timedelta(minutes=10),
            is_used=False
        )
        print(f"Generated code for {email}: {code}")  # Log qo‘shildi
        return attrs

class VerifyCodeSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=6)

class SetNewPasswordSerializer(serializers.Serializer):
    verification_code = serializers.CharField(max_length=6)
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        code = attrs.get('verification_code')
        password = attrs.get('new_password')
        confirm_password = attrs.get('confirm_password')

        if password != confirm_password:
            raise serializers.ValidationError("Parollar mos emas.")

        if not re.match(r'^\d{6}$', code):
            raise serializers.ValidationError("Kod 6 ta raqamdan iborat bo‘lishi kerak.")

        try:
            reset = ResetCode.objects.get(code=code, is_used=False)
            if reset.is_expired():
                raise serializers.ValidationError("Kod muddati tugagan.")
        except ResetCode.DoesNotExist:
            raise serializers.ValidationError("Kod noto‘g‘ri yoki ishlatilgan.")

        attrs['user'] = reset.user
        attrs['verification_obj'] = reset
        return attrs
