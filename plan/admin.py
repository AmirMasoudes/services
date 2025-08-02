from django.contrib import admin
from django.utils.html import format_html
from .models import ConfingPlansModel


@admin.register(ConfingPlansModel)
class PlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'price_display', 'traffic_display', 'in_volume', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at', 'price')
    search_fields = ('name', 'description')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('اطلاعات پلن', {
            'fields': ('name', 'description')
        }),
        ('قیمت و مدت', {
            'fields': ('price', 'in_volume')
        }),
        ('حجم داده', {
            'fields': ('traffic_mb',)
        }),
        ('وضعیت', {
            'fields': ('is_active',)
        }),
        ('تاریخ‌ها', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def price_display(self, obj):
        """نمایش قیمت با فرمت مناسب"""
        return format_html('<strong>{:,}</strong> تومان', obj.price)
    price_display.short_description = 'قیمت'
    price_display.admin_order_field = 'price'
    
    def traffic_display(self, obj):
        """نمایش حجم داده"""
        if obj.traffic_mb > 0:
            if obj.traffic_mb >= 1024:
                return f"{obj.get_traffic_gb():.1f} GB"
            else:
                return f"{obj.traffic_mb} MB"
        return "نامحدود"
    traffic_display.short_description = 'حجم داده'
    
    actions = ['activate_plans', 'deactivate_plans', 'duplicate_plans']
    
    def activate_plans(self, request, queryset):
        """فعال‌سازی پلن‌های انتخاب شده"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} پلن فعال شد.')
    activate_plans.short_description = 'فعال‌سازی پلن‌های انتخاب شده'
    
    def deactivate_plans(self, request, queryset):
        """غیرفعال‌سازی پلن‌های انتخاب شده"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} پلن غیرفعال شد.')
    deactivate_plans.short_description = 'غیرفعال‌سازی پلن‌های انتخاب شده'
    
    def duplicate_plans(self, request, queryset):
        """تکثیر پلن‌های انتخاب شده"""
        for plan in queryset:
            plan.pk = None
            plan.name = f"{plan.name} (کپی)"
            plan.is_active = False
            plan.save()
        self.message_user(request, f'{queryset.count()} پلن تکثیر شد.')
    duplicate_plans.short_description = 'تکثیر پلن‌های انتخاب شده'
