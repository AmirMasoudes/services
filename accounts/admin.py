# accounts/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import UsersModel

@admin.register(UsersModel)
class CustomUserAdmin(UserAdmin):
    list_display = ('id_tel', 'username_tel', 'full_name', 'telegram_id', 'username', 'is_active', 'is_admin', 'is_staff')
    list_filter = ('is_active', 'is_admin', 'is_staff', 'created_at')
    search_fields = ('id_tel', 'username_tel', 'full_name', 'telegram_id', 'username')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        (None, {'fields': ('id_tel', 'username_tel', 'full_name', 'telegram_id', 'username', 'password')}),
        ('Permissions', {'fields': ('is_active', 'is_admin', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'created_at', 'updated_at')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('id_tel', 'username_tel', 'full_name', 'telegram_id', 'username', 'password1', 'password2'),
        }),
    )
