from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models


class FoydalanuvchiManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError('Email manzili kerak')
        if not username:
            raise ValueError('Foydalanuvchi nomi (username) kerak')
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser is_staff bo‘lishi kerak')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser is_superuser bo‘lishi kerak')

        return self.create_user(email, username, password, **extra_fields)


class Foydalanuvchi(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True, default='defaultuser')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = FoydalanuvchiManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']  # superuser yaratishda kerak bo‘ladi

    def __str__(self):
        return self.email
