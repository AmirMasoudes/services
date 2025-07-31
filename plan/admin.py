from django.contrib import admin
from .models import ConfingPlansModel

@admin.register(ConfingPlansModel)
class PlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'in_volume', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name',)
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
