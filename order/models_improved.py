"""
Improved Order Models with Missing Fields
"""
from django.db import models
from plan.models import ConfingPlansModel
from core.models import BaseModel, TimeStampMixin, SoftDeleteModel
from accounts.models import UsersModel
from datetime import timedelta
from django.utils import timezone


class OrderUserModel(BaseModel, TimeStampMixin, SoftDeleteModel):
    """Improved Order Model with Status Tracking"""
    STATUS_CHOICES = [
        ('pending', 'در انتظار پرداخت'),
        ('paid', 'پرداخت شده'),
        ('active', 'فعال'),
        ('expired', 'منقضی شده'),
        ('cancelled', 'لغو شده'),
        ('refunded', 'بازگشت وجه'),
    ]
    
    user = models.ForeignKey(UsersModel, on_delete=models.CASCADE, related_name="user_orders")
    # FIXED: Changed from OneToOne to ForeignKey to allow multiple orders per plan
    plan = models.ForeignKey(ConfingPlansModel, on_delete=models.CASCADE, related_name="orders")
    is_active = models.BooleanField(default=False)
    start_plane_at = models.DateTimeField(editable=False, null=True, blank=True)
    end_plane_at = models.DateTimeField(editable=False, null=True, blank=True)
    
    # NEW FIELDS
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text="وضعیت سفارش",
        db_index=True
    )
    order_number = models.CharField(
        max_length=50,
        unique=True,
        help_text="شماره سفارش",
        db_index=True
    )
    total_amount = models.PositiveIntegerField(help_text="مبلغ کل")
    paid_amount = models.PositiveIntegerField(default=0, help_text="مبلغ پرداخت شده")
    payment_method = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="روش پرداخت"
    )
    notes = models.TextField(blank=True, null=True, help_text="یادداشت‌ها")
    activated_at = models.DateTimeField(null=True, blank=True, help_text="زمان فعال‌سازی")
    cancelled_at = models.DateTimeField(null=True, blank=True, help_text="زمان لغو")
    cancelled_reason = models.TextField(blank=True, null=True, help_text="دلیل لغو")
    
    class Meta:
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['status', 'is_active']),
            models.Index(fields=['order_number']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        if not self.start_plane_at:
            self.start_plane_at = timezone.now()
        if not self.end_plane_at and self.plan:
            duration = getattr(self.plan, 'duration_days', 30)
            self.end_plane_at = self.start_plane_at + timedelta(days=duration)
        
        # Generate order number if not set
        if not self.order_number:
            import uuid
            self.order_number = f"ORD-{uuid.uuid4().hex[:8].upper()}"
        
        # Set total amount from plan if not set
        if not self.total_amount and self.plan:
            self.total_amount = self.plan.price
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Order {self.order_number} - {self.user.full_name} - {self.plan.name}"
    
    def is_expired(self):
        """Check if order is expired"""
        if not self.end_plane_at:
            return False
        return timezone.now() > self.end_plane_at
    
    def can_be_activated(self):
        """Check if order can be activated"""
        return self.status == 'paid' and not self.is_expired()
    
    def activate(self):
        """Activate the order"""
        if self.can_be_activated():
            self.status = 'active'
            self.is_active = True
            self.activated_at = timezone.now()
            self.save()
            return True
        return False
    
    def cancel(self, reason: str = ""):
        """Cancel the order"""
        if self.status not in ['cancelled', 'refunded']:
            self.status = 'cancelled'
            self.is_active = False
            self.cancelled_at = timezone.now()
            self.cancelled_reason = reason
            self.save()
            return True
        return False


class PayMentModel(BaseModel, TimeStampMixin, SoftDeleteModel):
    """Improved Payment Model"""
    STATUS_CHOICES = [
        ('pending', 'در انتظار بررسی'),
        ('approved', 'تایید شده'),
        ('rejected', 'رد شده'),
        ('refunded', 'بازگشت وجه'),
    ]
    
    user = models.ForeignKey(UsersModel, on_delete=models.CASCADE, related_name="user_payments")
    order = models.ForeignKey(OrderUserModel, on_delete=models.CASCADE, related_name="payments")
    images = models.ImageField(upload_to='payments/')
    code_pay = models.IntegerField(help_text="کد پرداخت", db_index=True)
    is_active = models.BooleanField(default=True)
    rejected = models.BooleanField(default=False)
    
    # NEW FIELDS
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text="وضعیت پرداخت",
        db_index=True
    )
    amount = models.PositiveIntegerField(help_text="مبلغ پرداخت")
    payment_date = models.DateTimeField(null=True, blank=True, help_text="تاریخ پرداخت")
    approved_at = models.DateTimeField(null=True, blank=True, help_text="زمان تایید")
    approved_by = models.ForeignKey(
        UsersModel,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_payments",
        help_text="تایید کننده"
    )
    rejection_reason = models.TextField(blank=True, null=True, help_text="دلیل رد")
    notes = models.TextField(blank=True, null=True, help_text="یادداشت‌ها")
    
    class Meta:
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['order', 'status']),
            models.Index(fields=['code_pay']),
            models.Index(fields=['status', 'created_at']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Payment {self.code_pay} - {self.user.full_name} - {self.amount}"
    
    def approve(self, approver: UsersModel, notes: str = ""):
        """Approve the payment"""
        if self.status == 'pending':
            self.status = 'approved'
            self.is_active = True
            self.rejected = False
            self.approved_at = timezone.now()
            self.approved_by = approver
            self.notes = notes
            self.save()
            
            # Activate the order
            if self.order:
                self.order.status = 'paid'
                self.order.paid_amount = self.amount
                self.order.payment_method = 'manual'
                self.order.save()
                self.order.activate()
            
            return True
        return False
    
    def reject(self, reason: str = ""):
        """Reject the payment"""
        if self.status == 'pending':
            self.status = 'rejected'
            self.is_active = False
            self.rejected = True
            self.rejection_reason = reason
            self.save()
            return True
        return False

