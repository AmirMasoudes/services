from django.contrib import admin
from django.contrib.admin import AdminSite
from django.utils.translation import gettext_lazy as _


class ConfigVPNSite(AdminSite):
    """سایت ادمین سفارشی برای سیستم مدیریت VPN"""
    
    site_header = _('سیستم مدیریت VPN')
    site_title = _('پنل ادمین VPN')
    index_title = _('داشبورد مدیریت VPN')
    
    # تنظیمات اضافی
    site_url = '/'
    enable_nav_sidebar = True


# ایجاد نمونه از سایت ادمین سفارشی
admin_site = ConfigVPNSite(name='configvpn_admin')

# تنظیم سایت ادمین پیش‌فرض
admin.site.site_header = _('سیستم مدیریت VPN')
admin.site.site_title = _('پنل ادمین VPN')
admin.site.index_title = _('داشبورد مدیریت VPN') 