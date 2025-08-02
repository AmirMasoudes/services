from django.contrib import admin
from django.utils.html import format_html
from .models import MessageDirectory, MessageModel


class MessageInline(admin.TabularInline):
    model = MessageModel
    extra = 0
    readonly_fields = ('created_at', 'updated_at')
    fields = ('messages', 'created_at')
    can_delete = False


@admin.register(MessageDirectory)
class DirectoryAdmin(admin.ModelAdmin):
    list_display = ('admin_display', 'user_display', 'message_count', 'last_message', 'created_at')
    list_filter = ('created_at', 'admin', 'user')
    search_fields = ('admin__full_name', 'user__full_name', 'admin__username_tel', 'user__username_tel')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at', 'message_count_display')
    inlines = [MessageInline]
    
    fieldsets = (
        ('اطلاعات چت', {
            'fields': ('admin', 'user')
        }),
        ('آمار پیام‌ها', {
            'fields': ('message_count_display',)
        }),
        ('تاریخ‌ها', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def admin_display(self, obj):
        """نمایش اطلاعات ادمین"""
        if obj.admin:
            return format_html(
                '<strong>{}</strong><br><small>@{}</small>',
                obj.admin.full_name,
                obj.admin.username_tel
            )
        return '-'
    admin_display.short_description = 'ادمین'
    admin_display.admin_order_field = 'admin__full_name'
    
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
    
    def message_count(self, obj):
        """تعداد پیام‌ها"""
        return obj.messages.count()
    message_count.short_description = 'تعداد پیام‌ها'
    message_count.admin_order_field = 'messages__count'
    
    def message_count_display(self, obj):
        """نمایش تعداد پیام‌ها در فیلد"""
        count = self.message_count(obj)
        return format_html('<strong>{}</strong> پیام', count)
    message_count_display.short_description = 'تعداد پیام‌ها'
    
    def last_message(self, obj):
        """آخرین پیام"""
        last_msg = obj.messages.order_by('-created_at').first()
        if last_msg:
            return format_html(
                '<small>{}</small><br><span style="color: #666;">{}</span>',
                last_msg.created_at.strftime('%Y-%m-%d %H:%M'),
                last_msg.messages[:50] + '...' if len(last_msg.messages) > 50 else last_msg.messages
            )
        return '-'
    last_message.short_description = 'آخرین پیام'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('admin', 'user').prefetch_related('messages')
    
    actions = ['delete_all_messages']
    
    def delete_all_messages(self, request, queryset):
        """حذف تمام پیام‌های چت‌های انتخاب شده"""
        count = 0
        for directory in queryset:
            count += directory.messages.count()
            directory.messages.all().delete()
        self.message_user(request, f'{count} پیام حذف شد.')
    delete_all_messages.short_description = 'حذف تمام پیام‌های چت‌های انتخاب شده'


@admin.register(MessageModel)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('directory_display', 'message_preview', 'created_at')
    list_filter = ('created_at', 'directory__admin', 'directory__user')
    search_fields = ('messages', 'directory__admin__full_name', 'directory__user__full_name')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('اطلاعات چت', {
            'fields': ('directory',)
        }),
        ('پیام', {
            'fields': ('messages',)
        }),
        ('تاریخ‌ها', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def directory_display(self, obj):
        """نمایش اطلاعات چت"""
        if obj.directory:
            return format_html(
                '<strong>{}</strong> ↔ <strong>{}</strong><br><small>@{}</small> ↔ <small>@{}</small>',
                obj.directory.admin.full_name if obj.directory.admin else '-',
                obj.directory.user.full_name if obj.directory.user else '-',
                obj.directory.admin.username_tel if obj.directory.admin else '-',
                obj.directory.user.username_tel if obj.directory.user else '-'
            )
        return '-'
    directory_display.short_description = 'چت'
    
    def message_preview(self, obj):
        """پیش‌نمایش پیام"""
        if obj.messages:
            preview = obj.messages[:100]
            if len(obj.messages) > 100:
                preview += '...'
            return format_html(
                '<div style="max-width: 300px; overflow: hidden; text-overflow: ellipsis;">{}</div>',
                preview
            )
        return '-'
    message_preview.short_description = 'پیش‌نمایش پیام'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('directory__admin', 'directory__user')
    
    actions = ['delete_selected_messages']
    
    def delete_selected_messages(self, request, queryset):
        """حذف پیام‌های انتخاب شده"""
        count = queryset.count()
        queryset.delete()
        self.message_user(request, f'{count} پیام حذف شد.')
    delete_selected_messages.short_description = 'حذف پیام‌های انتخاب شده'
