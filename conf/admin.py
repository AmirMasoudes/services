from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import ConfigUserModel, TrialConfigModel


@admin.register(ConfigUserModel)
class ConfigAdmin(admin.ModelAdmin):
    list_display = ('user_display', 'order_display', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('user__full_name', 'user__username_tel', 'config', 'order__plans__name')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('اطلاعات کاربر', {
            'fields': ('user',)
        }),
        ('اطلاعات سفارش', {
            'fields': ('order',)
        }),
        ('کانفیگ', {
            'fields': ('config',)
        }),
        ('وضعیت', {
            'fields': ('is_active',)
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
    
    def order_display(self, obj):
        """نمایش اطلاعات سفارش"""
        if obj.order and obj.order.plans:
            return format_html(
                '<strong>{}</strong><br><small>{:,} تومان</small>',
                obj.order.plans.name,
                obj.order.plans.price
            )
        return '-'
    order_display.short_description = 'سفارش'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'order__plans')
    
    actions = ['activate_configs', 'deactivate_configs']
    
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


@admin.register(TrialConfigModel)
class TrialConfigAdmin(admin.ModelAdmin):
    list_display = ('user_display', 'is_active', 'expires_at', 'remaining_time', 'created_at')
    list_filter = ('is_active', 'created_at', 'expires_at')
    search_fields = ('user__full_name', 'user__username_tel', 'config')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at', 'remaining_time_display')
    
    fieldsets = (
        ('اطلاعات کاربر', {
            'fields': ('user',)
        }),
        ('کانفیگ تستی', {
            'fields': ('config',)
        }),
        ('وضعیت و انقضا', {
            'fields': ('is_active', 'expires_at', 'remaining_time_display')
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
        return super().get_queryset(request).select_related('user')
    
    actions = ['activate_trials', 'deactivate_trials', 'extend_trials_7_days']
    
    def activate_trials(self, request, queryset):
        """فعال‌سازی کانفیگ‌های تستی انتخاب شده"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} کانفیگ تستی فعال شد.')
    activate_trials.short_description = 'فعال‌سازی کانفیگ‌های تستی انتخاب شده'
    
    def deactivate_trials(self, request, queryset):
        """غیرفعال‌سازی کانفیگ‌های تستی انتخاب شده"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} کانفیگ تستی غیرفعال شد.')
    deactivate_trials.short_description = 'غیرفعال‌سازی کانفیگ‌های تستی انتخاب شده'
    
    def extend_trials_7_days(self, request, queryset):
        """تمدید کانفیگ‌های تستی به مدت 7 روز"""
        from datetime import timedelta
        updated = 0
        for trial in queryset:
            trial.expires_at += timedelta(days=7)
            trial.save()
            updated += 1
        self.message_user(request, f'{updated} کانفیگ تستی 7 روز تمدید شد.')
    extend_trials_7_days.short_description = 'تمدید 7 روزه کانفیگ‌های تستی انتخاب شده'
