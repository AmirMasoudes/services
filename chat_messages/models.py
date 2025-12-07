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
        admin_username = self.admin.username if self.admin and self.admin.username else 'N/A'
        user_username = self.user.username if self.user and self.user.username else 'N/A'
        return f"{admin_username} ↔ {user_username}"


class MessageModel(BaseModel, SoftDeleteModel, TimeStampMixin):
    directory = models.ForeignKey(
        MessageDirectory, on_delete=models.CASCADE, related_name="messages"
    )
    messages = models.TextField()

    def __str__(self):
        return f"Message #{self.id} - {self.directory}"
