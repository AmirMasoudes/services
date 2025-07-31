from core.models import TimeStampMixin, BaseModel, SoftDeleteModel
from django.db import models
from accounts.models import UsersModel
from order.models import OrderUserModel

class ConfigUserModel(BaseModel, TimeStampMixin, SoftDeleteModel):
    user = models.ForeignKey(UsersModel, on_delete=models.CASCADE, related_name="user_config")
    order = models.ForeignKey(OrderUserModel, on_delete=models.CASCADE, related_name="config_order")
    config = models.CharField(max_length=255)  # ✅ افزودن max_length
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user} - {self.order} - {self.config}"

class TrialConfigModel(BaseModel, TimeStampMixin, SoftDeleteModel):
    """کانفیگ تستی برای کاربران"""
    user = models.OneToOneField(UsersModel, on_delete=models.CASCADE, related_name="trial_config")
    config = models.TextField(help_text="کانفیگ تستی کاربر")
    is_active = models.BooleanField(default=True)
    expires_at = models.DateTimeField(help_text="تاریخ انقضای کانفیگ تستی")
    
    def __str__(self):
        return f"کانفیگ تستی {self.user.get_display_name()}"
    
    def is_expired(self):
        """آیا کانفیگ تستی منقضی شده است؟"""
        from django.utils import timezone
        return timezone.now() > self.expires_at
    
    def get_remaining_time(self):
        """زمان باقی‌مانده تا انقضا"""
        from django.utils import timezone
        from datetime import timedelta
        
        now = timezone.now()
        if now > self.expires_at:
            return timedelta(0)
        return self.expires_at - now
