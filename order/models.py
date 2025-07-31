from django.db import models
from plan.models import ConfingPlansModel
from core.models import BaseModel, TimeStampMixin, SoftDeleteModel
from accounts.models import UsersModel
from datetime import timedelta
from django.utils import timezone

class OrderUserModel(BaseModel, TimeStampMixin, SoftDeleteModel):
    user = models.ForeignKey(UsersModel, on_delete=models.CASCADE, related_name="user_order")
    plans = models.OneToOneField(ConfingPlansModel, on_delete=models.CASCADE, related_name="user_plans")
    is_active = models.BooleanField(default=False)
    start_plane_at = models.DateTimeField(editable=False)
    end_plane_at = models.DateTimeField(editable=False)

    def save(self, *args, **kwargs):
        if not self.start_plane_at:
            self.start_plane_at = timezone.now()
        if not self.end_plane_at:
            self.end_plane_at = self.start_plane_at + timedelta(days=30)
        super().save(*args, **kwargs)


class PayMentModel(BaseModel, TimeStampMixin, SoftDeleteModel):
    user = models.ForeignKey(UsersModel, on_delete=models.CASCADE, related_name="user_payment")
    order = models.ForeignKey(OrderUserModel, on_delete=models.CASCADE, related_name="user_plan")
    images = models.ImageField(upload_to='payments/')
    code_pay = models.IntegerField()
    is_active = models.BooleanField(default=True)
    rejected = models.BooleanField(default=False)
