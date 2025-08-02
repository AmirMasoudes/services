from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from datetime import timedelta


@staff_member_required
def admin_dashboard(request):
    """داشبورد ادمین برای سیستم مدیریت VPN"""
    
    # آمار کلی
    from accounts.models import UsersModel
    from xui_servers.models import XUIServer, UserConfig
    from plan.models import ConfingPlansModel
    from order.models import OrderUserModel, PayMentModel
    from conf.models import TrialConfigModel
    
    stats = {
        'total_users': UsersModel.objects.count(),
        'active_users': UsersModel.objects.filter(is_active=True).count(),
        'total_servers': XUIServer.objects.count(),
        'active_servers': XUIServer.objects.filter(is_active=True).count(),
        'total_configs': UserConfig.objects.count(),
        'active_configs': UserConfig.objects.filter(is_active=True).count(),
        'expired_configs': UserConfig.objects.filter(expires_at__lt=timezone.now()).count(),
        'total_plans': ConfingPlansModel.objects.count(),
        'active_plans': ConfingPlansModel.objects.filter(is_active=True).count(),
        'total_orders': OrderUserModel.objects.count(),
        'active_orders': OrderUserModel.objects.filter(is_active=True).count(),
        'total_payments': PayMentModel.objects.count(),
        'approved_payments': PayMentModel.objects.filter(is_active=True, rejected=False).count(),
        'pending_payments': PayMentModel.objects.filter(is_active=False, rejected=False).count(),
        'rejected_payments': PayMentModel.objects.filter(rejected=True).count(),
        'total_trials': TrialConfigModel.objects.count(),
        'active_trials': TrialConfigModel.objects.filter(is_active=True).count(),
    }
    
    # کاربران جدید در 7 روز گذشته
    week_ago = timezone.now() - timedelta(days=7)
    new_users_week = UsersModel.objects.filter(created_at__gte=week_ago).count()
    
    # کانفیگ‌های در حال انقضا
    future_date = timezone.now() + timedelta(days=7)
    expiring_configs = UserConfig.objects.filter(
        expires_at__gte=timezone.now(),
        expires_at__lte=future_date,
        is_active=True
    )
    
    # سفارش‌های جدید
    new_orders_week = OrderUserModel.objects.filter(created_at__gte=week_ago).count()
    
    # پرداخت‌های در انتظار
    pending_payments = PayMentModel.objects.filter(is_active=False, rejected=False).count()
    
    # کانفیگ‌های منقضی شده
    expired_configs = UserConfig.objects.filter(
        expires_at__lt=timezone.now(),
        is_active=True
    )
    
    context = {
        'stats': stats,
        'new_users_week': new_users_week,
        'expiring_configs': expiring_configs,
        'new_orders_week': new_orders_week,
        'pending_payments': pending_payments,
        'expired_configs': expired_configs,
        'current_time': timezone.now(),
    }
    
    return render(request, 'admin/dashboard.html', context)


def home(request):
    """صفحه اصلی"""
    return render(request, 'home.html')
