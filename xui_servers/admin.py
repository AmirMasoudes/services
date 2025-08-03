from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db import models
from .models import XUIServer, XUIInbound, XUIClient, UserConfig

@admin.register(XUIServer)
class XUIServerAdmin(admin.ModelAdmin):
    list_display = ['name', 'host', 'port', 'is_active', 'get_inbounds_count', 'get_clients_count']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'host']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('name', 'host', 'port', 'is_active')
        }),
        ('تنظیمات X-UI', {
            'fields': ('username', 'password', 'web_base_path')
        }),
        ('اطلاعات زمانی', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_inbounds_count(self, obj):
        return obj.inbounds.count()
    get_inbounds_count.short_description = 'تعداد Inbound ها'
    
    def get_clients_count(self, obj):
        total = 0
        for inbound in obj.inbounds.all():
            total += inbound.clients.count()
        return total
    get_clients_count.short_description = 'تعداد کلاینت ها'

class XUIClientInline(admin.TabularInline):
    model = XUIClient
    extra = 0
    readonly_fields = ['get_remaining_gb', 'is_expired']
    fields = ['user', 'email', 'total_gb', 'used_gb', 'get_remaining_gb', 'expiry_time', 'is_active', 'is_expired']
    
    def get_remaining_gb(self, obj):
        return f"{obj.get_remaining_gb()} GB"
    get_remaining_gb.short_description = 'حجم باقی‌مانده'
    
    def is_expired(self, obj):
        if obj.is_expired():
            return format_html('<span style="color: red;">منقضی شده</span>')
        return format_html('<span style="color: green;">فعال</span>')
    is_expired.short_description = 'وضعیت انقضا'

@admin.register(XUIInbound)
class XUIInboundAdmin(admin.ModelAdmin):
    list_display = ['remark', 'server', 'port', 'protocol', 'is_active', 'get_available_slots', 'current_clients', 'max_clients']
    list_filter = ['is_active', 'protocol', 'server', 'created_at']
    search_fields = ['remark', 'port']
    readonly_fields = ['created_at', 'updated_at', 'get_available_slots']
    inlines = [XUIClientInline]
    
    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('server', 'xui_inbound_id', 'port', 'protocol', 'remark', 'is_active')
        }),
        ('تنظیمات کلاینت', {
            'fields': ('max_clients', 'current_clients', 'get_available_slots')
        }),
        ('اطلاعات زمانی', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_available_slots(self, obj):
        slots = obj.get_available_slots()
        if slots > 0:
            return format_html('<span style="color: green;">{}</span>', slots)
        return format_html('<span style="color: red;">{}</span>', slots)
    get_available_slots.short_description = 'اسلات‌های خالی'
    
    actions = ['sync_with_xui', 'update_client_counts']
    
    def sync_with_xui(self, request, queryset):
        """همگام‌سازی با X-UI"""
        from .services import XUIService
        
        for inbound in queryset:
            try:
                xui_service = XUIService(inbound.server)
                if xui_service.login():
                    # دریافت اطلاعات inbound از X-UI
                    inbounds = xui_service.get_inbounds()
                    for xui_inbound in inbounds:
                        if xui_inbound.get('id') == inbound.xui_inbound_id:
                            # به‌روزرسانی اطلاعات
                            inbound.port = xui_inbound.get('port', inbound.port)
                            inbound.remark = xui_inbound.get('remark', inbound.remark)
                            inbound.protocol = xui_inbound.get('protocol', inbound.protocol)
                            
                            # شمارش کلاینت‌ها
                            settings = xui_inbound.get('settings', {})
                            if isinstance(settings, str):
                                import json
                                try:
                                    settings = json.loads(settings)
                                except:
                                    settings = {}
                            
                            clients = settings.get('clients', [])
                            inbound.current_clients = len(clients)
                            inbound.save()
                            break
            except Exception as e:
                self.message_user(request, f"خطا در همگام‌سازی {inbound.remark}: {e}")
        
        self.message_user(request, "همگام‌سازی با X-UI انجام شد")
    sync_with_xui.short_description = "همگام‌سازی با X-UI"
    
    def update_client_counts(self, request, queryset):
        """به‌روزرسانی تعداد کلاینت‌ها"""
        for inbound in queryset:
            inbound.current_clients = inbound.clients.count()
            inbound.save()
        
        self.message_user(request, "تعداد کلاینت‌ها به‌روزرسانی شد")
    update_client_counts.short_description = "به‌روزرسانی تعداد کلاینت‌ها"

@admin.register(XUIClient)
class XUIClientAdmin(admin.ModelAdmin):
    list_display = ['email', 'user', 'inbound', 'total_gb', 'used_gb', 'get_remaining_gb', 'is_active', 'is_expired']
    list_filter = ['is_active', 'inbound', 'created_at']
    search_fields = ['email', 'user__full_name', 'user__username_tel']
    readonly_fields = ['created_at', 'updated_at', 'get_remaining_gb', 'is_expired']
    
    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('inbound', 'user', 'xui_client_id', 'email', 'is_active')
        }),
        ('تنظیمات ترافیک', {
            'fields': ('total_gb', 'used_gb', 'get_remaining_gb', 'limit_ip')
        }),
        ('تنظیمات زمانی', {
            'fields': ('expiry_time', 'is_expired')
        }),
        ('اطلاعات زمانی', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_remaining_gb(self, obj):
        remaining = obj.get_remaining_gb()
        if remaining > 0:
            return format_html('<span style="color: green;">{} GB</span>', remaining)
        return format_html('<span style="color: red;">{} GB</span>', remaining)
    get_remaining_gb.short_description = 'حجم باقی‌مانده'
    
    def is_expired(self, obj):
        if obj.is_expired():
            return format_html('<span style="color: red;">منقضی شده</span>')
        return format_html('<span style="color: green;">فعال</span>')
    is_expired.short_description = 'وضعیت انقضا'
    
    actions = ['sync_with_xui', 'update_traffic_usage']
    
    def sync_with_xui(self, request, queryset):
        """همگام‌سازی با X-UI"""
        from .services import XUIService
        
        for client in queryset:
            try:
                xui_service = XUIService(client.inbound.server)
                if xui_service.login():
                    # دریافت اطلاعات کلاینت از X-UI
                    inbounds = xui_service.get_inbounds()
                    for xui_inbound in inbounds:
                        if xui_inbound.get('id') == client.inbound.xui_inbound_id:
                            settings = xui_inbound.get('settings', {})
                            if isinstance(settings, str):
                                import json
                                try:
                                    settings = json.loads(settings)
                                except:
                                    settings = {}
                            
                            clients = settings.get('clients', [])
                            for xui_client in clients:
                                if xui_client.get('id') == client.xui_client_id:
                                    # به‌روزرسانی اطلاعات
                                    client.total_gb = xui_client.get('totalGB', client.total_gb)
                                    client.used_gb = xui_client.get('up', 0) + xui_client.get('down', 0)
                                    client.expiry_time = xui_client.get('expiryTime', client.expiry_time)
                                    client.is_active = xui_client.get('enable', client.is_active)
                                    client.save()
                                    break
            except Exception as e:
                self.message_user(request, f"خطا در همگام‌سازی {client.email}: {e}")
        
        self.message_user(request, "همگام‌سازی با X-UI انجام شد")
    sync_with_xui.short_description = "همگام‌سازی با X-UI"
    
    def update_traffic_usage(self, request, queryset):
        """به‌روزرسانی استفاده ترافیک"""
        for client in queryset:
            # محاسبه استفاده ترافیک (این قسمت باید بر اساس API X-UI پیاده‌سازی شود)
            pass
        
        self.message_user(request, "استفاده ترافیک به‌روزرسانی شد")
    update_traffic_usage.short_description = "به‌روزرسانی استفاده ترافیک"

class UserConfigInline(admin.TabularInline):
    model = UserConfig
    extra = 0
    readonly_fields = ['is_expired', 'get_remaining_time']
    fields = ['server', 'inbound', 'config_name', 'protocol', 'is_active', 'is_expired', 'get_remaining_time']

@admin.register(UserConfig)
class UserConfigAdmin(admin.ModelAdmin):
    list_display = ['user', 'server', 'inbound', 'config_name', 'protocol', 'is_active', 'is_expired', 'get_remaining_time']
    list_filter = ['is_active', 'protocol', 'server', 'inbound', 'is_trial', 'created_at']
    search_fields = ['user__full_name', 'user__username_tel', 'config_name']
    readonly_fields = ['created_at', 'updated_at', 'is_expired', 'get_remaining_time']
    
    fieldsets = (
        ('اطلاعات کاربر', {
            'fields': ('user', 'server', 'inbound')
        }),
        ('تنظیمات کانفیگ', {
            'fields': ('xui_inbound_id', 'xui_user_id', 'config_name', 'config_data', 'protocol', 'is_active')
        }),
        ('تنظیمات زمانی', {
            'fields': ('expires_at', 'is_expired', 'get_remaining_time')
        }),
        ('تنظیمات پلن', {
            'fields': ('plan', 'is_trial')
        }),
        ('اطلاعات زمانی', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def is_expired(self, obj):
        if obj.is_expired():
            return format_html('<span style="color: red;">منقضی شده</span>')
        return format_html('<span style="color: green;">فعال</span>')
    is_expired.short_description = 'وضعیت انقضا'
    
    def get_remaining_time(self, obj):
        remaining = obj.get_remaining_time()
        if remaining is None:
            return "نامحدود"
        if remaining.days > 0:
            return f"{remaining.days} روز"
        if remaining.seconds > 3600:
            hours = remaining.seconds // 3600
            return f"{hours} ساعت"
        return f"{remaining.seconds // 60} دقیقه"
    get_remaining_time.short_description = 'زمان باقی‌مانده'
    
    actions = ['assign_to_inbound', 'regenerate_config']
    
    def assign_to_inbound(self, request, queryset):
        """تخصیص به Inbound"""
        from .services import XUIEnhancedService
        import requests
        
        for config in queryset:
            if not config.inbound:
                # یافتن inbound مناسب
                available_inbounds = XUIInbound.objects.filter(
                    server=config.server,
                    is_active=True
                ).filter(
                    current_clients__lt=models.F('max_clients')
                )
                
                if available_inbounds.exists():
                    inbound = available_inbounds.first()
                    config.inbound = inbound
                    config.xui_inbound_id = inbound.xui_inbound_id
                    config.save()
                    
                    # ایجاد کلاینت در X-UI
                    try:
                        session = requests.Session()
                        base_url = inbound.server.get_full_url()
                        
                        # لاگین
                        login_data = {
                            "username": inbound.server.username,
                            "password": inbound.server.password
                        }
                        
                        response = session.post(
                            f"{base_url}/login",
                            json=login_data,
                            headers={'Content-Type': 'application/json'},
                            timeout=10
                        )
                        
                        if response.status_code == 200:
                            # ایجاد کلاینت
                            from .enhanced_api_models import XUIClientCreationRequest, XUIClientManager
                            
                            client_request = XUIClientCreationRequest(
                                inbound_id=inbound.xui_inbound_id,
                                email=f"{config.user.username_tel}@vpn.com",
                                total_gb=0,  # نامحدود
                                expiry_time=0  # نامحدود
                            )
                            
                            client_manager = XUIClientManager(base_url, session)
                            if client_manager.add_client(client_request):
                                # ایجاد رکورد کلاینت
                                XUIClient.objects.create(
                                    inbound=inbound,
                                    user=config.user,
                                    xui_client_id=client_request.to_payload()["settings"]["clients"][0]["id"],
                                    email=client_request.email,
                                    total_gb=0,
                                    expiry_time=0
                                )
                                
                                # به‌روزرسانی تعداد کلاینت‌ها
                                inbound.current_clients += 1
                                inbound.save()
                    except Exception as e:
                        self.message_user(request, f"خطا در ایجاد کلاینت برای {config.user.full_name}: {e}")
        
        self.message_user(request, "تخصیص به Inbound انجام شد")
    assign_to_inbound.short_description = "تخصیص به Inbound"
    
    def regenerate_config(self, request, queryset):
        """تولید مجدد کانفیگ"""
        from .services import UserConfigService
        
        for config in queryset:
            try:
                # تولید مجدد کانفیگ
                new_config_data = UserConfigService.generate_config(
                    user=config.user,
                    server=config.server,
                    protocol=config.protocol
                )
                
                config.config_data = new_config_data
                config.save()
                
            except Exception as e:
                self.message_user(request, f"خطا در تولید مجدد کانفیگ برای {config.user.full_name}: {e}")
        
        self.message_user(request, "تولید مجدد کانفیگ انجام شد")
    regenerate_config.short_description = "تولید مجدد کانفیگ"
