#!/usr/bin/env python3
import os
import sys
import django

# تنظیم Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

def create_xui_admin():
    """ایجاد ادمین برای X-UI service"""
    print("�� ایجاد ادمین برای X-UI service...")
    
    # 1. بررسی مدل‌های موجود
    from xui_servers.models import XUIServer, UserConfig
    
    print("📊 مدل‌های موجود:")
    print(f"  - XUIServer: {XUIServer.objects.count()} رکورد")
    print(f"  - UserConfig: {UserConfig.objects.count()} رکورد")
    
    # 2. ایجاد ادمین برای XUIServer
    admin_content = '''from django.contrib import admin
from .models import XUIServer, UserConfig

@admin.register(XUIServer)
class XUIServerAdmin(admin.ModelAdmin):
    """ادمین برای سرورهای X-UI"""
    list_display = ('name', 'host', 'port', 'username', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'host', 'username')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('name', 'host', 'port', 'username', 'password')
        }),
        ('وضعیت', {
            'fields': ('is_active',)
        }),
        ('زمان‌بندی', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
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
    list_display = ('user', 'server', 'config_name', 'protocol', 'is_trial', 'is_active', 'created_at', 'expires_at')
    list_filter = ('protocol', 'is_trial', 'is_active', 'created_at', 'expires_at', 'server')
    search_fields = ('user__full_name', 'user__username_tel', 'config_name', 'config_data')
    readonly_fields = ('created_at', 'updated_at', 'xui_inbound_id', 'xui_user_id')
    
    fieldsets = (
        ('اطلاعات کاربر', {
            'fields': ('user', 'server')
        }),
        ('اطلاعات کانفیگ', {
            'fields': ('config_name', 'protocol', 'config_data')
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
    
    def get_queryset(self, request):
        """نمایش همه کانفیگ‌ها"""
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

# تنظیمات اضافی برای ادمین
admin.site.site_header = "پنل مدیریت VPN"
admin.site.site_title = "مدیریت VPN"
admin.site.index_title = "خوش آمدید به پنل مدیریت VPN"
'''
    
    # نوشتن فایل ادمین
    with open('xui_servers/admin.py', 'w', encoding='utf-8') as f:
        f.write(admin_content)
    
    print("✅ فایل xui_servers/admin.py ایجاد شد!")
    
    # 3. بررسی اپلیکیشن در settings
    try:
        from config.settings import INSTALLED_APPS
        if 'xui_servers' not in INSTALLED_APPS:
            print("⚠️ xui_servers در INSTALLED_APPS نیست")
        else:
            print("✅ xui_servers در INSTALLED_APPS موجود است")
    except Exception as e:
        print(f"❌ خطا در بررسی settings: {e}")
    
    # 4. ایجاد superuser (اگر وجود ندارد)
    try:
        from django.contrib.auth.models import User
        if not User.objects.filter(is_superuser=True).exists():
            print("�� ایجاد superuser...")
            User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
            print("✅ superuser ایجاد شد:")
            print("  - نام کاربری: admin")
            print("  - رمز عبور: admin123")
        else:
            print("✅ superuser موجود است")
    except Exception as e:
        print(f"❌ خطا در ایجاد superuser: {e}")
    
    # 5. نمایش اطلاعات
    print("\n📊 اطلاعات ادمین:")
    print("  - آدرس: http://127.0.0.1:8000/admin/")
    print("  - نام کاربری: admin")
    print("  - رمز عبور: admin123")
    print("\n📋 قابلیت‌های ادمین:")
    print("  - مدیریت سرورهای X-UI")
    print("  - مدیریت کانفیگ‌های کاربران")
    print("  - مشاهده آمار و وضعیت")
    print("  - حذف خودکار از X-UI")
    
    print("\n�� ادمین X-UI service آماده است!")

if __name__ == "__main__":
    create_xui_admin() 