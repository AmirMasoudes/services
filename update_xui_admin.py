#!/usr/bin/env python3
import os
import sys
import django

# تنظیم Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

def update_xui_admin():
    """به‌روزرسانی ادمین X-UI"""
    print("🔧 به‌روزرسانی ادمین X-UI...")
    
    # محتوای جدید برای admin.py
    admin_content = '''from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import XUIServer, UserConfig

@admin.register(XUIServer)
class XUIServerAdmin(admin.ModelAdmin):
    """ادمین برای سرورهای X-UI"""
    list_display = ('name', 'host', 'port', 'username', 'status_display', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'host', 'username')
    readonly_fields = ('created_at', 'updated_at', 'status_display')
    list_per_page = 20
    
    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('name', 'host', 'port', 'username', 'password')
        }),
        ('وضعیت', {
            'fields': ('is_active', 'status_display')
        }),
        ('زمان‌بندی', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def status_display(self, obj):
        """نمایش وضعیت سرور"""
        if obj.is_active:
            return format_html('<span style="color: green;">✅ فعال</span>')
        else:
            return format_html('<span style="color: red;">❌ غیرفعال</span>')
    status_display.short_description = 'وضعیت'
    
    def get_queryset(self, request):
        """نمایش همه سرورها"""
        return super().get_queryset(request)
    
    def save_model(self, request, obj, form, change):
        """ذخیره مدل با لاگ"""
        if change:
            self.log_change(request, obj, "تغییر سرور X-UI")
        else:
            self.log_addition(request, obj, "افزودن سرور X-UI جدید")
        super().save_model(request, obj, form, change)

@admin.register(UserConfig)
class UserConfigAdmin(admin.ModelAdmin):
    """ادمین برای کانفیگ‌های کاربران"""
    list_display = ('user_info', 'server', 'config_name', 'protocol_display', 'trial_status', 'active_status', 'created_at', 'expires_at')
    list_filter = ('protocol', 'is_trial', 'is_active', 'created_at', 'expires_at', 'server')
    search_fields = ('user__full_name', 'user__username_tel', 'config_name', 'config_data')
    readonly_fields = ('created_at', 'updated_at', 'xui_inbound_id', 'xui_user_id', 'config_preview')
    list_per_page = 25
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('اطلاعات کاربر', {
            'fields': ('user', 'server')
        }),
        ('اطلاعات کانفیگ', {
            'fields': ('config_name', 'protocol', 'config_data', 'config_preview')
        }),
        ('وضعیت', {
            'fields': ('is_trial', 'is_active', 'plan')
        }),
        ('اطلاعات X-UI', {
            'fields': ('xui_inbound_id', 'xui_user_id'),
            'classes': ('collapse',)
        }),
        ('زمان‌بندی', {
            'fields': ('created_at', 'updated_at', 'expires_at'),
            'classes': ('collapse',)
        }),
    )
    
    def user_info(self, obj):
        """نمایش اطلاعات کاربر"""
        if obj.user:
            return format_html(
                '<strong>{}</strong><br><small>@{}</small>',
                obj.user.full_name or 'نامشخص',
                obj.user.username_tel or 'نامشخص'
            )
        return 'نامشخص'
    user_info.short_description = 'کاربر'
    
    def protocol_display(self, obj):
        """نمایش پروتکل"""
        colors = {
            'vless': 'blue',
            'vmess': 'green',
            'trojan': 'orange',
            'shadowsocks': 'purple'
        }
        color = colors.get(obj.protocol, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.protocol.upper()
        )
    protocol_display.short_description = 'پروتکل'
    
    def trial_status(self, obj):
        """نمایش وضعیت تستی"""
        if obj.is_trial:
            return format_html('<span style="color: orange;">🎁 تستی</span>')
        else:
            return format_html('<span style="color: blue;">💳 پولی</span>')
    trial_status.short_description = 'نوع'
    
    def active_status(self, obj):
        """نمایش وضعیت فعال"""
        if obj.is_active:
            return format_html('<span style="color: green;">✅ فعال</span>')
        else:
            return format_html('<span style="color: red;">❌ غیرفعال</span>')
    active_status.short_description = 'وضعیت'
    
    def config_preview(self, obj):
        """پیش‌نمایش کانفیگ"""
        if obj.config_data:
            preview = obj.config_data[:100] + '...' if len(obj.config_data) > 100 else obj.config_data
            return format_html('<code style="background: #f5f5f5; padding: 2px 4px; border-radius: 3px;">{}</code>', preview)
        return 'بدون کانفیگ'
    config_preview.short_description = 'پیش‌نمایش کانفیگ'
    
    def get_queryset(self, request):
        """نمایش همه کانفیگ‌ها با بهینه‌سازی"""
        return super().get_queryset(request).select_related('user', 'server', 'plan')
    
    def save_model(self, request, obj, form, change):
        """ذخیره مدل با لاگ"""
        if change:
            self.log_change(request, obj, "تغییر کانفیگ کاربر")
        else:
            self.log_addition(request, obj, "افزودن کانفیگ جدید")
        super().save_model(request, obj, form, change)
    
    def delete_model(self, request, obj):
        """حذف کانفیگ از X-UI"""
        try:
            from .services import XUIService
            xui_service = XUIService(obj.server)
            if xui_service.login():
                xui_service.delete_client(obj.xui_inbound_id, f"{obj.user.telegram_id}@example.com")
        except Exception as e:
            print(f"خطا در حذف از X-UI: {e}")
        
        self.log_deletion(request, obj, "حذف کانفیگ کاربر")
        super().delete_model(request, obj)
    
    actions = ['activate_configs', 'deactivate_configs', 'delete_expired']
    
    def activate_configs(self, request, queryset):
        """فعال‌سازی کانفیگ‌های انتخاب شده"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} کانفیگ فعال شد.')
    activate_configs.short_description = "فعال‌سازی کانفیگ‌های انتخاب شده"
    
    def deactivate_configs(self, request, queryset):
        """غیرفعال‌سازی کانفیگ‌های انتخاب شده"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} کانفیگ غیرفعال شد.')
    deactivate_configs.short_description = "غیرفعال‌سازی کانفیگ‌های انتخاب شده"
    
    def delete_expired(self, request, queryset):
        """حذف کانفیگ‌های منقضی شده"""
        from django.utils import timezone
        expired = queryset.filter(expires_at__lt=timezone.now())
        count = expired.count()
        expired.delete()
        self.message_user(request, f'{count} کانفیگ منقضی شده حذف شد.')
    delete_expired.short_description = "حذف کانفیگ‌های منقضی شده"

# تنظیمات اضافی برای ادمین
admin.site.site_header = "پنل مدیریت VPN"
admin.site.site_title = "مدیریت VPN"
admin.site.index_title = "خوش آمدید به پنل مدیریت VPN"

# اضافه کردن آمار به صفحه اصلی
def get_admin_stats():
    """دریافت آمار برای نمایش در صفحه اصلی"""
    from django.utils import timezone
    from datetime import timedelta
    
    total_users = UserConfig.objects.count()
    active_users = UserConfig.objects.filter(is_active=True).count()
    trial_users = UserConfig.objects.filter(is_trial=True).count()
    paid_users = UserConfig.objects.filter(is_trial=False).count()
    expired_users = UserConfig.objects.filter(expires_at__lt=timezone.now()).count()
    
    return {
        'total_users': total_users,
        'active_users': active_users,
        'trial_users': trial_users,
        'paid_users': paid_users,
        'expired_users': expired_users,
    }

# اضافه کردن آمار به context
admin.site.index_template = 'admin/index_with_stats.html'
'''
    
    # نوشتن فایل ادمین
    with open('xui_servers/admin.py', 'w', encoding='utf-8') as f:
        f.write(admin_content)
    
    print("✅ فایل xui_servers/admin.py به‌روزرسانی شد!")
    
    # ایجاد template برای نمایش آمار
    template_content = '''{% extends "admin/index.html" %}
{% load i18n %}

{% block content %}
<div class="module">
    <h2>�� آمار کلی سیستم</h2>
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0;">
        <div style="background: #e3f2fd; padding: 15px; border-radius: 8px; text-align: center;">
            <h3 style="color: #1976d2; margin: 0;">👥 کل کاربران</h3>
            <p style="font-size: 24px; font-weight: bold; margin: 10px 0;">{{ total_users }}</p>
        </div>
        <div style="background: #e8f5e8; padding: 15px; border-radius: 8px; text-align: center;">
            <h3 style="color: #388e3c; margin: 0;">✅ کاربران فعال</h3>
            <p style="font-size: 24px; font-weight: bold; margin: 10px 0;">{{ active_users }}</p>
        </div>
        <div style="background: #fff3e0; padding: 15px; border-radius: 8px; text-align: center;">
            <h3 style="color: #f57c00; margin: 0;">�� کاربران تستی</h3>
            <p style="font-size: 24px; font-weight: bold; margin: 10px 0;">{{ trial_users }}</p>
        </div>
        <div style="background: #f3e5f5; padding: 15px; border-radius: 8px; text-align: center;">
            <h3 style="color: #7b1fa2; margin: 0;">�� کاربران پولی</h3>
            <p style="font-size: 24px; font-weight: bold; margin: 10px 0;">{{ paid_users }}</p>
        </div>
        <div style="background: #ffebee; padding: 15px; border-radius: 8px; text-align: center;">
            <h3 style="color: #d32f2f; margin: 0;">⏰ کاربران منقضی</h3>
            <p style="font-size: 24px; font-weight: bold; margin: 10px 0;">{{ expired_users }}</p>
        </div>
    </div>
</div>
{{ block.super }}
{% endblock %}
'''
    
    # ایجاد پوشه templates اگر وجود ندارد
    os.makedirs('templates/admin', exist_ok=True)
    
    # نوشتن template
    with open('templates/admin/index_with_stats.html', 'w', encoding='utf-8') as f:
        f.write(template_content)
    
    print("✅ Template آمار ایجاد شد!")
    
    # نمایش اطلاعات
    print("\n📊 اطلاعات ادمین:")
    print("  - آدرس: http://127.0.0.1:8000/admin/")
    print("  - نام کاربری: admin")
    print("  - رمز عبور: admin123")
    print("\n📋 قابلیت‌های جدید:")
    print("  - نمایش وضعیت با رنگ‌بندی")
    print("  - پیش‌نمایش کانفیگ‌ها")
    print("  - آمار کلی سیستم")
    print("  - عملیات گروهی (فعال/غیرفعال/حذف)")
    print("  - فیلتر و جستجوی پیشرفته")
    
    print("\n�� ادمین X-UI service به‌روزرسانی شد!")

if __name__ == "__main__":
    update_xui_admin() 