from core.models import TimeStampMixin, BaseModel, SoftDeleteModel
from django.db import models


class ConfingPlansModel(BaseModel, TimeStampMixin, SoftDeleteModel):
    name = models.CharField(max_length=100)
    price = models.PositiveIntegerField()
    in_volume = models.PositiveIntegerField()
