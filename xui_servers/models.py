from django.db import models
from core.models import BaseModel, TimeStampMixin, SoftDeleteModel
from accounts.models import UsersModel
from order.models import OrderUserModel
from conf.models import TrialConfigModel
from plan.models import ConfingPlansModel


class AuditLog(BaseModel, TimeStampMixin):
    """Audit Log for tracking changes"""
    ACTION_CHOICES = [
        ('create', 'ایجاد'),
        ('update', 'به‌روزرسانی'),
        ('delete', 'حذف'),
        ('activate', 'فعال‌سازی'),
        ('deactivate', 'غیرفعال‌سازی'),
        ('sync', 'همگام‌سازی'),
        ('provision', 'تامین'),
        ('deprovision', 'حذف تامین'),
    ]
    
    user = models.ForeignKey(
        UsersModel,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="کاربر انجام‌دهنده"
    )
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, help_text="عمل انجام شده")
    model_name = models.CharField(max_length=100, help_text="نام مدل")
    object_id = models.CharField(max_length=100, help_text="شناسه شی")
    description = models.TextField(help_text="توضیحات")
    changes = models.JSONField(null=True, blank=True, help_text="تغییرات")
    ip_address = models.GenericIPAddressField(null=True, blank=True, help_text="آدرس IP")
    
    class Meta:
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['model_name', 'object_id']),
            models.Index(fields=['action', 'created_at']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.action} {self.model_name} {self.object_id} by {self.user}"

class XUIServer(BaseModel, TimeStampMixin, SoftDeleteModel):
    """Improved X-UI Server Model"""
    SERVER_TYPE_CHOICES = [
        ('xui', 'X-UI'),
        ('sui', 'S-UI'),
    ]
    HEALTH_STATUS_CHOICES = [
        ('healthy', 'سالم'),
        ('unhealthy', 'ناسالم'),
        ('unknown', 'نامشخص'),
    ]
    
    name = models.CharField(max_length=100, help_text="نام سرور")
    host = models.CharField(max_length=255, help_text="آدرس سرور")
    port = models.IntegerField(default=54321, help_text="پورت X-UI")
    username = models.CharField(max_length=100, help_text="نام کاربری X-UI")
    password = models.CharField(max_length=255, help_text="رمز عبور X-UI")
    web_base_path = models.CharField(max_length=100, default="/MsxZ4xuIy5xLfQtsSC/", help_text="مسیر وب X-UI")
    is_active = models.BooleanField(default=True, help_text="آیا سرور فعال است؟")
    
    # NEW FIELDS
    use_ssl = models.BooleanField(default=True, help_text="استفاده از HTTPS")
    server_type = models.CharField(
        max_length=20,
        choices=SERVER_TYPE_CHOICES,
        default='xui',
        help_text="نوع سرور"
    )
    api_token = models.CharField(max_length=255, blank=True, null=True, help_text="API Token برای S-UI")
    health_check_enabled = models.BooleanField(default=True, help_text="فعال بودن بررسی سلامت")
    last_health_check = models.DateTimeField(null=True, blank=True, help_text="آخرین بررسی سلامت")
    health_status = models.CharField(
        max_length=20,
        choices=HEALTH_STATUS_CHOICES,
        default='unknown',
        help_text="وضعیت سلامت"
    )
    last_sync_at = models.DateTimeField(null=True, blank=True, help_text="آخرین همگام‌سازی")
    sync_interval_minutes = models.IntegerField(default=15, help_text="فاصله همگام‌سازی (دقیقه)")
    
    class Meta:
        indexes = [
            models.Index(fields=['is_active', 'is_deleted']),
            models.Index(fields=['server_type']),
            models.Index(fields=['health_status']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.host}:{self.port})"
    
    def get_full_url(self):
        """دریافت URL کامل سرور"""
        protocol = "https" if self.use_ssl else "http"
        return f"{protocol}://{self.host}:{self.port}{self.web_base_path}"

class XUIInbound(BaseModel, TimeStampMixin, SoftDeleteModel):
    """Improved Inbound Model"""
    server = models.ForeignKey(XUIServer, on_delete=models.CASCADE, related_name="inbounds")
    xui_inbound_id = models.IntegerField(help_text="شناسه inbound در X-UI", db_index=True)
    port = models.IntegerField(help_text="پورت inbound")
    protocol = models.CharField(max_length=20, default="vless", help_text="پروتکل (vless, vmess, trojan)")
    remark = models.CharField(max_length=100, help_text="نام inbound")
    is_active = models.BooleanField(default=True, help_text="آیا inbound فعال است؟")
    max_clients = models.IntegerField(default=100, help_text="حداکثر تعداد کلاینت")
    current_clients = models.IntegerField(default=0, help_text="تعداد کلاینت‌های فعلی")
    
    # NEW FIELDS
    stream_settings = models.JSONField(null=True, blank=True, help_text="تنظیمات Stream")
    sniffing_settings = models.JSONField(null=True, blank=True, help_text="تنظیمات Sniffing")
    last_sync_at = models.DateTimeField(null=True, blank=True, help_text="آخرین همگام‌سازی")
    
    class Meta:
        indexes = [
            models.Index(fields=['server', 'is_active']),
            models.Index(fields=['protocol', 'is_active']),
            models.Index(fields=['xui_inbound_id']),
        ]
        unique_together = [['server', 'xui_inbound_id']]
    
    def __str__(self):
        return f"{self.remark} (پورت: {self.port}, پروتکل: {self.protocol})"
    
    def get_available_slots(self):
        """تعداد اسلات‌های خالی"""
        return self.max_clients - self.current_clients
    
    def can_accept_client(self):
        """آیا می‌تواند کلاینت جدید بپذیرد؟"""
        return self.is_active and self.current_clients < self.max_clients

class XUIClient(BaseModel, TimeStampMixin, SoftDeleteModel):
    """Improved Client Model"""
    inbound = models.ForeignKey(XUIInbound, on_delete=models.CASCADE, related_name="clients")
    user = models.ForeignKey(UsersModel, on_delete=models.CASCADE, related_name="xui_clients")
    xui_client_id = models.CharField(max_length=100, help_text="شناسه کلاینت در X-UI", db_index=True)
    email = models.CharField(max_length=100, help_text="ایمیل کلاینت", db_index=True)
    total_gb = models.BigIntegerField(default=0, help_text="حجم کل (GB)")
    used_gb = models.BigIntegerField(default=0, help_text="حجم استفاده شده (GB)")
    expiry_time = models.BigIntegerField(default=0, help_text="زمان انقضا")
    limit_ip = models.IntegerField(default=0, help_text="محدودیت IP")
    is_active = models.BooleanField(default=True, help_text="آیا کلاینت فعال است؟")
    
    # NEW FIELDS
    last_usage_sync = models.DateTimeField(null=True, blank=True, help_text="آخرین همگام‌سازی استفاده")
    sync_retry_count = models.IntegerField(default=0, help_text="تعداد تلاش برای همگام‌سازی")
    last_sync_error = models.TextField(blank=True, null=True, help_text="آخرین خطای همگام‌سازی")
    
    class Meta:
        indexes = [
            models.Index(fields=['inbound', 'is_active']),
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['email']),
            models.Index(fields=['is_active', 'expiry_time']),
        ]
    
    def __str__(self):
        return f"{self.email} - {self.inbound.remark}"
    
    def get_remaining_gb(self):
        """حجم باقی‌مانده"""
        return max(0, self.total_gb - self.used_gb)
    
    def is_expired(self):
        """آیا منقضی شده است؟"""
        from django.utils import timezone
        if self.expiry_time == 0:
            return False
        return timezone.now().timestamp() * 1000 > self.expiry_time

class UserConfig(BaseModel, TimeStampMixin, SoftDeleteModel):
    """Improved User Config Model"""
    STATUS_CHOICES = [
        ('pending', 'در انتظار'),
        ('active', 'فعال'),
        ('expired', 'منقضی شده'),
        ('suspended', 'معلق'),
        ('cancelled', 'لغو شده'),
    ]
    
    user = models.ForeignKey(UsersModel, on_delete=models.CASCADE, related_name="xui_configs")
    server = models.ForeignKey(XUIServer, on_delete=models.CASCADE, related_name="user_configs")
    inbound = models.ForeignKey(XUIInbound, on_delete=models.CASCADE, related_name="user_configs", null=True, blank=True)
    xui_inbound_id = models.IntegerField(help_text="شناسه inbound در X-UI", db_index=True)
    xui_user_id = models.CharField(max_length=100, help_text="شناسه کاربر در X-UI", db_index=True)
    config_name = models.CharField(max_length=100, help_text="نام کانفیگ")
    config_data = models.TextField(help_text="داده‌های کانفیگ (vmess/vless)")
    is_active = models.BooleanField(default=True, help_text="آیا کانفیگ فعال است؟")
    expires_at = models.DateTimeField(null=True, blank=True, help_text="تاریخ انقضا", db_index=True)
    protocol = models.CharField(max_length=20, default="vless", help_text="پروتکل کانفیگ")
    plan = models.ForeignKey(ConfingPlansModel, on_delete=models.SET_NULL, null=True, blank=True, help_text="پلن مرتبط")
    is_trial = models.BooleanField(default=False, help_text="آیا کانفیگ تستی است؟")
    
    # NEW FIELDS
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text="وضعیت کانفیگ"
    )
    subscription_url = models.URLField(blank=True, null=True, help_text="لینک اشتراک")
    last_sync_at = models.DateTimeField(null=True, blank=True, help_text="آخرین همگام‌سازی")
    sync_required = models.BooleanField(default=False, help_text="نیاز به همگام‌سازی")
    provision_retry_count = models.IntegerField(default=0, help_text="تعداد تلاش برای تامین")
    last_provision_error = models.TextField(blank=True, null=True, help_text="آخرین خطای تامین")
    external_id = models.CharField(max_length=255, blank=True, null=True, help_text="شناسه خارجی برای idempotency", db_index=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['user', 'status']),
            models.Index(fields=['expires_at', 'is_active']),
            models.Index(fields=['sync_required']),
            models.Index(fields=['xui_inbound_id', 'xui_user_id']),
            models.Index(fields=['external_id']),
        ]
    
    def __str__(self):
        return f"{self.user.get_display_name()} - {self.config_name}"
    
    def is_expired(self):
        """آیا کانفیگ منقضی شده است؟"""
        if not self.expires_at:
            return False
        from django.utils import timezone
        return timezone.now() > self.expires_at
    
    def get_remaining_time(self):
        """زمان باقی‌مانده تا انقضا"""
        if not self.expires_at:
            return None
        from django.utils import timezone
        from datetime import timedelta
        
        now = timezone.now()
        if now > self.expires_at:
            return timedelta(0)
        return self.expires_at - now
