from core.models import TimeStampMixin, BaseModel, SoftDeleteModel
from django.db import models


class ConfingPlansModel(BaseModel, TimeStampMixin, SoftDeleteModel):
    name = models.CharField(max_length=100)
    price = models.PositiveIntegerField()
    in_volume = models.PositiveIntegerField()
    traffic_mb = models.PositiveIntegerField(default=0, help_text="حجم داده به مگابایت")
    is_active = models.BooleanField(default=True, help_text="آیا پلن فعال است؟")
    description = models.TextField(blank=True, null=True, help_text="توضیحات پلن")
    
    def __str__(self):
        return f"{self.name} - {self.price:,} تومان"
    
    def get_traffic_gb(self):
        """تبدیل حجم داده به گیگابایت"""
        return self.traffic_mb / 1024 if self.traffic_mb > 0 else 0
