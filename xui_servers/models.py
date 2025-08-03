from django.db import models
from core.models import BaseModel, TimeStampMixin, SoftDeleteModel
from accounts.models import UsersModel
from order.models import OrderUserModel
from conf.models import TrialConfigModel
from plan.models import ConfingPlansModel

class XUIServer(BaseModel, TimeStampMixin, SoftDeleteModel):
    """سرور X-UI"""
    name = models.CharField(max_length=100, help_text="نام سرور")
    host = models.CharField(max_length=255, help_text="آدرس سرور")
    port = models.IntegerField(default=54321, help_text="پورت X-UI")
    username = models.CharField(max_length=100, help_text="نام کاربری X-UI")
    password = models.CharField(max_length=255, help_text="رمز عبور X-UI")
    web_base_path = models.CharField(max_length=100, default="/MsxZ4xuIy5xLfQtsSC/", help_text="مسیر وب X-UI")
    is_active = models.BooleanField(default=True, help_text="آیا سرور فعال است؟")
    
    def __str__(self):
        return f"{self.name} ({self.host}:{self.port})"
    
    def get_full_url(self):
        """دریافت URL کامل سرور"""
        return f"http://{self.host}:{self.port}{self.web_base_path}"

class XUIInbound(BaseModel, TimeStampMixin, SoftDeleteModel):
    """Inbound های X-UI"""
    server = models.ForeignKey(XUIServer, on_delete=models.CASCADE, related_name="inbounds")
    xui_inbound_id = models.IntegerField(help_text="شناسه inbound در X-UI")
    port = models.IntegerField(help_text="پورت inbound")
    protocol = models.CharField(max_length=20, default="vless", help_text="پروتکل (vless, vmess, trojan)")
    remark = models.CharField(max_length=100, help_text="نام inbound")
    is_active = models.BooleanField(default=True, help_text="آیا inbound فعال است؟")
    max_clients = models.IntegerField(default=100, help_text="حداکثر تعداد کلاینت")
    current_clients = models.IntegerField(default=0, help_text="تعداد کلاینت‌های فعلی")
    
    def __str__(self):
        return f"{self.remark} (پورت: {self.port}, پروتکل: {self.protocol})"
    
    def get_available_slots(self):
        """تعداد اسلات‌های خالی"""
        return self.max_clients - self.current_clients
    
    def can_accept_client(self):
        """آیا می‌تواند کلاینت جدید بپذیرد؟"""
        return self.is_active and self.current_clients < self.max_clients

class XUIClient(BaseModel, TimeStampMixin, SoftDeleteModel):
    """کلاینت‌های X-UI"""
    inbound = models.ForeignKey(XUIInbound, on_delete=models.CASCADE, related_name="clients")
    user = models.ForeignKey(UsersModel, on_delete=models.CASCADE, related_name="xui_clients")
    xui_client_id = models.CharField(max_length=100, help_text="شناسه کلاینت در X-UI")
    email = models.CharField(max_length=100, help_text="ایمیل کلاینت")
    total_gb = models.BigIntegerField(default=0, help_text="حجم کل (GB)")
    used_gb = models.BigIntegerField(default=0, help_text="حجم استفاده شده (GB)")
    expiry_time = models.BigIntegerField(default=0, help_text="زمان انقضا")
    limit_ip = models.IntegerField(default=0, help_text="محدودیت IP")
    is_active = models.BooleanField(default=True, help_text="آیا کلاینت فعال است؟")
    
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
    """کانفیگ کاربر در X-UI"""
    user = models.ForeignKey(UsersModel, on_delete=models.CASCADE, related_name="xui_configs")
    server = models.ForeignKey(XUIServer, on_delete=models.CASCADE, related_name="user_configs")
    inbound = models.ForeignKey(XUIInbound, on_delete=models.CASCADE, related_name="user_configs", null=True, blank=True)
    xui_inbound_id = models.IntegerField(help_text="شناسه inbound در X-UI")
    xui_user_id = models.CharField(max_length=100, help_text="شناسه کاربر در X-UI")  # تغییر به CharField
    config_name = models.CharField(max_length=100, help_text="نام کانفیگ")
    config_data = models.TextField(help_text="داده‌های کانفیگ (vmess/vless)")
    is_active = models.BooleanField(default=True, help_text="آیا کانفیگ فعال است؟")
    expires_at = models.DateTimeField(null=True, blank=True, help_text="تاریخ انقضا")
    protocol = models.CharField(max_length=20, default="vless", help_text="پروتکل کانفیگ")
    plan = models.ForeignKey(ConfingPlansModel, on_delete=models.SET_NULL, null=True, blank=True, help_text="پلن مرتبط")
    is_trial = models.BooleanField(default=False, help_text="آیا کانفیگ تستی است؟")
    
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
