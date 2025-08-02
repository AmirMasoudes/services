from core.models import TimeStampMixin, BaseModel, SoftDeleteModel
from django.db import models
import locale


class ConfingPlansModel(BaseModel, TimeStampMixin, SoftDeleteModel):
    name = models.CharField(max_length=100)
    price = models.PositiveIntegerField()
    in_volume = models.PositiveIntegerField()
    traffic_mb = models.PositiveIntegerField(default=0, help_text="حجم داده به مگابایت")
    is_active = models.BooleanField(default=True, help_text="آیا پلن فعال است؟")
    description = models.TextField(blank=True, null=True, help_text="توضیحات پلن")
    
    def __str__(self):
        if self.price is not None:
            try:
                # Use locale formatting for better compatibility
                formatted_price = locale.format_string("%d", int(self.price), grouping=True)
                return f"{self.name} - {formatted_price} تومان"
            except (ValueError, TypeError):
                # Fallback to simple formatting
                return f"{self.name} - {str(self.price)} تومان"
        return f"{self.name} - نامشخص تومان"
    
    def get_traffic_gb(self):
        """تبدیل حجم داده به گیگابایت"""
        return self.traffic_mb / 1024 if self.traffic_mb > 0 else 0
