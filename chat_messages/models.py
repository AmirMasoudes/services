from django.db import models
from accounts.models import UsersModel
from core.models import BaseModel, SoftDeleteModel, TimeStampMixin


class MessageDirectory(BaseModel, SoftDeleteModel, TimeStampMixin):
    admin = models.ForeignKey(
        UsersModel, on_delete=models.CASCADE, related_name="admin_directories"
    )
    user = models.ForeignKey(
        UsersModel, on_delete=models.CASCADE, related_name="user_directories"
    )

    def __str__(self):
        return f"{self.admin.username} ↔ {self.user.username}"


class MessageModel(BaseModel, SoftDeleteModel, TimeStampMixin):
    directory = models.ForeignKey(
        MessageDirectory, on_delete=models.CASCADE, related_name="messages"
    )
    messages = models.TextField()

    def __str__(self):
        return f"Message #{self.id} - {self.directory}"
