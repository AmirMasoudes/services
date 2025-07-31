from django.contrib import admin
from .models import ConfigUserModel

@admin.register(ConfigUserModel)
class ConfigAdmin(admin.ModelAdmin):
    list_display = ('user', 'order', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('user__full_name', 'user__username_tel', 'config')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
