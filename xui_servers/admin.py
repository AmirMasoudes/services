from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from django.db.models import Q
from .models import XUIServer, UserConfig


@admin.register(XUIServer)
class XUIServerAdmin(admin.ModelAdmin):
    list_display = ('name', 'host', 'port', 'username', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'host', 'username')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('اطلاعات سرور', {
            'fields': ('name', 'host', 'port', 'username', 'password')
        }),
        ('وضعیت', {
            'fields': ('is_active',)
        }),
        ('تاریخ‌ها', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related()


class UserConfigInline(admin.TabularInline):
    model = UserConfig
    extra = 0
    readonly_fields = ('created_at', 'updated_at')
    fields = ('config_name', 'server', 'is_active', 'expires_at', 'protocol', 'plan', 'is_trial')
    can_delete = False


@admin.register(UserConfig)
class UserConfigAdmin(admin.ModelAdmin):
    list_display = ('user_display', 'server', 'config_name', 'protocol', 'is_active', 'expires_at', 'is_trial', 'remaining_time')
    list_filter = ('is_active', 'is_trial', 'protocol', 'server', 'created_at', 'expires_at')
    search_fields = ('user__full_name', 'user__username_tel', 'config_name', 'server__name')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at', 'remaining_time_display')
    
    fieldsets = (
        ('اطلاعات کاربر', {
            'fields': ('user', 'server')
        }),
        ('کانفیگ', {
            'fields': ('config_name', 'xui_inbound_id', 'xui_user_id', 'config_data', 'protocol')
        }),
        ('پلن و وضعیت', {
            'fields': ('plan', 'is_active', 'is_trial')
        }),
        ('تاریخ انقضا', {
            'fields': ('expires_at', 'remaining_time_display')
        }),
        ('تاریخ‌ها', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def user_display(self, obj):
        """نمایش اطلاعات کاربر"""
        if obj.user:
            return format_html(
                '<strong>{}</strong><br><small>@{}</small>',
                obj.user.full_name,
                obj.user.username_tel
            )
        return '-'
    user_display.short_description = 'کاربر'
    user_display.admin_order_field = 'user__full_name'
    
    def remaining_time(self, obj):
        """زمان باقی‌مانده"""
        if obj.expires_at:
            remaining = obj.get_remaining_time()
            if remaining:
                days = remaining.days
                hours = remaining.seconds // 3600
                if days > 0:
                    return f"{days} روز"
                elif hours > 0:
                    return f"{hours} ساعت"
                else:
                    return "کمتر از 1 ساعت"
            else:
                return "منقضی شده"
        return "بدون انقضا"
    remaining_time.short_description = 'زمان باقی‌مانده'
    
    def remaining_time_display(self, obj):
        """نمایش زمان باقی‌مانده در فیلد"""
        remaining = self.remaining_time(obj)
        if "منقضی شده" in remaining:
            return format_html('<span style="color: red;">{}</span>', remaining)
        elif "کمتر از 1 ساعت" in remaining:
            return format_html('<span style="color: orange;">{}</span>', remaining)
        else:
            return format_html('<span style="color: green;">{}</span>', remaining)
    remaining_time_display.short_description = 'زمان باقی‌مانده'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'server', 'plan')
    
    def get_list_filter(self, request):
        """فیلترهای اضافی برای ادمین"""
        list_filter = list(super().get_list_filter(request))
        list_filter.append('expires_at')
        return list_filter
    
    def get_search_fields(self, request):
        """فیلدهای جستجو"""
        search_fields = list(super().get_search_fields(request))
        search_fields.extend(['user__telegram_id', 'server__host'])
        return search_fields
    
    actions = ['activate_configs', 'deactivate_configs', 'mark_as_trial', 'mark_as_paid']
    
    def activate_configs(self, request, queryset):
        """فعال‌سازی کانفیگ‌های انتخاب شده"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} کانفیگ فعال شد.')
    activate_configs.short_description = 'فعال‌سازی کانفیگ‌های انتخاب شده'
    
    def deactivate_configs(self, request, queryset):
        """غیرفعال‌سازی کانفیگ‌های انتخاب شده"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} کانفیگ غیرفعال شد.')
    deactivate_configs.short_description = 'غیرفعال‌سازی کانفیگ‌های انتخاب شده'
    
    def mark_as_trial(self, request, queryset):
        """علامت‌گذاری به عنوان تستی"""
        updated = queryset.update(is_trial=True)
        self.message_user(request, f'{updated} کانفیگ به عنوان تستی علامت‌گذاری شد.')
    mark_as_trial.short_description = 'علامت‌گذاری به عنوان تستی'
    
    def mark_as_paid(self, request, queryset):
        """علامت‌گذاری به عنوان پولی"""
        updated = queryset.update(is_trial=False)
        self.message_user(request, f'{updated} کانفیگ به عنوان پولی علامت‌گذاری شد.')
    mark_as_paid.short_description = 'علامت‌گذاری به عنوان پولی'
