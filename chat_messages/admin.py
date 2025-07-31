from django.contrib import admin
from .models import MessageDirectory, MessageModel

@admin.register(MessageDirectory)
class DirectoryAdmin(admin.ModelAdmin):
    list_display = ('admin', 'user', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('admin__full_name', 'user__full_name')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')

@admin.register(MessageModel)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('directory', 'messages', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('directory__admin__full_name', 'directory__user__full_name', 'messages')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
