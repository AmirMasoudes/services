from django.contrib import admin
from .models import OrderUserModel, PayMentModel

@admin.register(OrderUserModel)
class OrderUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'plans', 'is_active', 'start_plane_at', 'end_plane_at', 'created_at')
    list_filter = ('is_active', 'created_at', 'plans')
    search_fields = ('user__full_name', 'user__username_tel', 'plans__name')
    ordering = ('-created_at',)
    readonly_fields = ('start_plane_at', 'end_plane_at', 'created_at', 'updated_at')

@admin.register(PayMentModel)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'order', 'code_pay', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('user__full_name', 'user__username_tel', 'code_pay')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
