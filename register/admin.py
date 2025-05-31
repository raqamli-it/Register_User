from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import Foydalanuvchi

@admin.register(Foydalanuvchi)
class FoydalanuvchiAdmin(BaseUserAdmin):
    ordering = ['id']
    list_display = ['email', 'is_staff', 'is_active']
    search_fields = ['email']
    readonly_fields = ['last_login']

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )

    # Chunki USERNAME_FIELD = 'email'
    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.add_fieldsets
        return super().get_fieldsets(request, obj)
