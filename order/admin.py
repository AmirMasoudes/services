from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import OrderUserModel, PayMentModel


class PaymentInline(admin.TabularInline):
    model = PayMentModel
    extra = 0
    readonly_fields = ('created_at', 'updated_at')
    fields = ('images', 'code_pay', 'is_active', 'rejected')
    can_delete = False


@admin.register(OrderUserModel)
class OrderUserAdmin(admin.ModelAdmin):
    list_display = ('user_display', 'plan_display', 'is_active', 'start_plane_at', 'end_plane_at', 'remaining_days', 'created_at')
    list_filter = ('is_active', 'created_at', 'plans', 'start_plane_at', 'end_plane_at')
    search_fields = ('user__full_name', 'user__username_tel', 'plans__name')
    ordering = ('-created_at',)
    readonly_fields = ('start_plane_at', 'end_plane_at', 'created_at', 'updated_at', 'remaining_days_display')
    inlines = [PaymentInline]
    
    fieldsets = (
        ('اطلاعات کاربر', {
            'fields': ('user',)
        }),
        ('اطلاعات پلن', {
            'fields': ('plans',)
        }),
        ('وضعیت سفارش', {
            'fields': ('is_active',)
        }),
        ('تاریخ‌های پلن', {
            'fields': ('start_plane_at', 'end_plane_at', 'remaining_days_display')
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
    
    def plan_display(self, obj):
        """نمایش اطلاعات پلن"""
        if obj.plans:
            return format_html(
                '<strong>{}</strong><br><small>{:,} تومان</small>',
                obj.plans.name,
                obj.plans.price
            )
        return '-'
    plan_display.short_description = 'پلن'
    plan_display.admin_order_field = 'plans__name'
    
    def remaining_days(self, obj):
        """روزهای باقی‌مانده"""
        if obj.end_plane_at:
            remaining = obj.end_plane_at - timezone.now()
            if remaining.days > 0:
                return f"{remaining.days} روز"
            elif remaining.days == 0:
                return "امروز"
            else:
                return "منقضی شده"
        return "بدون انقضا"
    remaining_days.short_description = 'روزهای باقی‌مانده'
    
    def remaining_days_display(self, obj):
        """نمایش روزهای باقی‌مانده در فیلد"""
        remaining = self.remaining_days(obj)
        if "منقضی شده" in remaining:
            return format_html('<span style="color: red;">{}</span>', remaining)
        elif "امروز" in remaining:
            return format_html('<span style="color: orange;">{}</span>', remaining)
        else:
            return format_html('<span style="color: green;">{}</span>', remaining)
    remaining_days_display.short_description = 'روزهای باقی‌مانده'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'plans')
    
    actions = ['activate_orders', 'deactivate_orders', 'extend_orders_30_days']
    
    def activate_orders(self, request, queryset):
        """فعال‌سازی سفارش‌های انتخاب شده"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} سفارش فعال شد.')
    activate_orders.short_description = 'فعال‌سازی سفارش‌های انتخاب شده'
    
    def deactivate_orders(self, request, queryset):
        """غیرفعال‌سازی سفارش‌های انتخاب شده"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} سفارش غیرفعال شد.')
    deactivate_orders.short_description = 'غیرفعال‌سازی سفارش‌های انتخاب شده'
    
    def extend_orders_30_days(self, request, queryset):
        """تمدید سفارش‌ها به مدت 30 روز"""
        from datetime import timedelta
        updated = 0
        for order in queryset:
            order.end_plane_at += timedelta(days=30)
            order.save()
            updated += 1
        self.message_user(request, f'{updated} سفارش 30 روز تمدید شد.')
    extend_orders_30_days.short_description = 'تمدید 30 روزه سفارش‌های انتخاب شده'


@admin.register(PayMentModel)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user_display', 'order_display', 'code_pay', 'payment_status', 'created_at')
    list_filter = ('is_active', 'rejected', 'created_at')
    search_fields = ('user__full_name', 'user__username_tel', 'code_pay', 'order__plans__name')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('اطلاعات کاربر', {
            'fields': ('user',)
        }),
        ('اطلاعات سفارش', {
            'fields': ('order',)
        }),
        ('اطلاعات پرداخت', {
            'fields': ('code_pay', 'images')
        }),
        ('وضعیت پرداخت', {
            'fields': ('is_active', 'rejected')
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
    
    def payment_status(self, obj):
        """وضعیت پرداخت"""
        if obj.rejected:
            return format_html('<span style="color: red;">رد شده</span>')
        elif obj.is_active:
            return format_html('<span style="color: green;">تایید شده</span>')
        else:
            return format_html('<span style="color: orange;">در انتظار</span>')
    payment_status.short_description = 'وضعیت پرداخت'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'order__plans')
    
    actions = ['approve_payments', 'reject_payments', 'mark_as_pending']
    
    def approve_payments(self, request, queryset):
        """تایید پرداخت‌های انتخاب شده"""
        updated = queryset.update(is_active=True, rejected=False)
        self.message_user(request, f'{updated} پرداخت تایید شد.')
    approve_payments.short_description = 'تایید پرداخت‌های انتخاب شده'
    
    def reject_payments(self, request, queryset):
        """رد پرداخت‌های انتخاب شده"""
        updated = queryset.update(is_active=False, rejected=True)
        self.message_user(request, f'{updated} پرداخت رد شد.')
    reject_payments.short_description = 'رد پرداخت‌های انتخاب شده'
    
    def mark_as_pending(self, request, queryset):
        """علامت‌گذاری به عنوان در انتظار"""
        updated = queryset.update(is_active=False, rejected=False)
        self.message_user(request, f'{updated} پرداخت در انتظار شد.')
    mark_as_pending.short_description = 'علامت‌گذاری به عنوان در انتظار'
