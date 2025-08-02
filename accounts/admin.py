# accounts/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.utils import timezone
from .models import UsersModel


@admin.register(UsersModel)
class CustomUserAdmin(UserAdmin):
    list_display = ('id_tel', 'username_tel', 'full_name', 'telegram_id', 'username', 'is_active', 'is_admin', 'is_staff', 'has_used_trial', 'user_status')
    list_filter = ('is_active', 'is_admin', 'is_staff', 'has_used_trial', 'created_at')
    search_fields = ('id_tel', 'username_tel', 'full_name', 'telegram_id', 'username')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at', 'user_status_display')
    
    fieldsets = (
        ('اطلاعات کاربر', {
            'fields': ('id_tel', 'username_tel', 'full_name', 'telegram_id', 'username', 'password')
        }),
        ('وضعیت کاربر', {
            'fields': ('is_active', 'has_used_trial', 'user_status_display')
        }),
        ('دسترسی‌ها', {
            'fields': ('is_admin', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('تاریخ‌ها', {
            'fields': ('last_login', 'created_at', 'updated_at')
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('id_tel', 'username_tel', 'full_name', 'telegram_id', 'username', 'password1', 'password2'),
        }),
    )
    
    def user_status(self, obj):
        """وضعیت کاربر"""
        if obj.is_admin:
            return format_html('<span style="color: #007bff;">ادمین</span>')
        elif obj.is_staff:
            return format_html('<span style="color: #28a745;">کارمند</span>')
        else:
            return format_html('<span style="color: #6c757d;">کاربر عادی</span>')
    user_status.short_description = 'وضعیت'
    
    def user_status_display(self, obj):
        """نمایش وضعیت کاربر در فیلد"""
        return self.user_status(obj)
    user_status_display.short_description = 'وضعیت کاربر'
    
    actions = ['activate_users', 'deactivate_users', 'mark_as_admin', 'mark_as_staff', 'mark_as_regular_user', 'reset_trial_status']
    
    def activate_users(self, request, queryset):
        """فعال‌سازی کاربران انتخاب شده"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} کاربر فعال شد.')
    activate_users.short_description = 'فعال‌سازی کاربران انتخاب شده'
    
    def deactivate_users(self, request, queryset):
        """غیرفعال‌سازی کاربران انتخاب شده"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} کاربر غیرفعال شد.')
    deactivate_users.short_description = 'غیرفعال‌سازی کاربران انتخاب شده'
    
    def mark_as_admin(self, request, queryset):
        """تبدیل به ادمین"""
        updated = queryset.update(is_admin=True, is_staff=True)
        self.message_user(request, f'{updated} کاربر به ادمین تبدیل شد.')
    mark_as_admin.short_description = 'تبدیل به ادمین'
    
    def mark_as_staff(self, request, queryset):
        """تبدیل به کارمند"""
        updated = queryset.update(is_staff=True, is_admin=False)
        self.message_user(request, f'{updated} کاربر به کارمند تبدیل شد.')
    mark_as_staff.short_description = 'تبدیل به کارمند'
    
    def mark_as_regular_user(self, request, queryset):
        """تبدیل به کاربر عادی"""
        updated = queryset.update(is_staff=False, is_admin=False)
        self.message_user(request, f'{updated} کاربر به کاربر عادی تبدیل شد.')
    mark_as_regular_user.short_description = 'تبدیل به کاربر عادی'
    
    def reset_trial_status(self, request, queryset):
        """بازنشانی وضعیت تستی"""
        updated = queryset.update(has_used_trial=False)
        self.message_user(request, f'{updated} وضعیت تستی بازنشانی شد.')
    reset_trial_status.short_description = 'بازنشانی وضعیت تستی'
