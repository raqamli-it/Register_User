from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Foydalanuvchi, ResetCode

class CustomUserAdmin(UserAdmin):
    model = Foydalanuvchi
    list_display = ('id', 'email', 'username', 'is_active', 'is_staff')
    list_filter = ('is_staff', 'is_active')
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser')}),
        ('Groups', {'fields': ('groups',)}),
        ('User Permissions', {'fields': ('user_permissions',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )
    search_fields = ('email',)
    ordering = ('email',)

admin.site.register(Foydalanuvchi, CustomUserAdmin)
admin.site.register(ResetCode)
