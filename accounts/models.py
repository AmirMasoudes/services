from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from core.models import BaseModel, SoftDeleteModel, TimeStampMixin

class UsersManager(BaseUserManager):
    def create_user(self, id_tel, username_tel, full_name, telegram_id=None, username=None):
        if not id_tel:
            raise ValueError("User must have an id_tel")
        user = self.model(
            id_tel=id_tel, 
            username_tel=username_tel, 
            full_name=full_name,
            telegram_id=telegram_id,
            username=username
        )
        user.set_unusable_password()  # پسورد بی‌استفاده برای کاربران معمولی
        user.save(using=self._db)
        return user

    def create_superuser(self, id_tel, username_tel, full_name, password, telegram_id=None, username=None):
        user = self.model(
            id_tel=id_tel, 
            username_tel=username_tel, 
            full_name=full_name,
            telegram_id=telegram_id,
            username=username
        )
        user.set_password(password)
        user.is_admin = True
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user

class UsersModel(AbstractBaseUser, PermissionsMixin, BaseModel, SoftDeleteModel, TimeStampMixin):
    id_tel = models.CharField(max_length=20, unique=True)
    username_tel = models.CharField(max_length=100)
    full_name = models.CharField(max_length=100)
    telegram_id = models.BigIntegerField(unique=True, null=True, blank=True)
    username = models.CharField(max_length=100, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)  # برای دسترسی به پنل ادمین
    has_used_trial = models.BooleanField(default=False, help_text="آیا کاربر از پلن تستی استفاده کرده است؟")

    objects = UsersManager()

    USERNAME_FIELD = 'id_tel'
    REQUIRED_FIELDS = ['username_tel', 'full_name']

    def __str__(self):
        return f"{self.full_name} (@{self.username or 'بدون یوزرنیم'})"
    
    def get_display_name(self):
        """نام نمایشی کاربر"""
        return self.full_name or f"کاربر {self.telegram_id}"
    
    def get_telegram_info(self):
        """اطلاعات تلگرام کاربر"""
        return {
            'id': self.telegram_id,
            'username': self.username,
            'full_name': self.full_name
        }
    
    def can_get_trial(self):
        """آیا کاربر می‌تواند پلن تستی بگیرد؟"""
        return not self.has_used_trial
    
    def mark_trial_used(self):
        """علامت‌گذاری استفاده از پلن تستی"""
        self.has_used_trial = True
        self.save()
