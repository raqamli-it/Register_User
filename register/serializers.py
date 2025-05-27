import re
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from .models import Foydalanuvchi

class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = Foydalanuvchi
        fields = ['email', 'username', 'password', 'password2']

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError("Parollar mos emas")
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        return Foydalanuvchi.objects.create_user(**validated_data)


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


class SetNewPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)
    token = serializers.CharField()
    uid = serializers.CharField()

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Parol kamida 8 ta belgidan iborat bo'lishi kerak.")
        if not re.search(r'\d', value):
            raise serializers.ValidationError("Parol kamida bitta raqam bo'lishi kerak.")
        if not re.search(r'[A-Za-z]', value):
            raise serializers.ValidationError("Parol kamida bitta harf bo'lishi kerak.")
        validate_password(value)
        return value

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Parollar mos kelmayapti.")
        return data
