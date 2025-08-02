"""
ماژول اکشن‌های ادمین برای سیستم مدیریت VPN
"""
from django.contrib import admin
from django.utils import timezone
from django.db.models import Q, Count, Sum
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


class AdminActionsMixin:
    """کلاس میکسین برای اکشن‌های ادمین"""
    
    def get_statistics(self, request):
        """دریافت آمار کلی سیستم"""
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
        return stats
    
    def bulk_extend_configs(self, request, queryset, days=30):
        """تمدید دسته‌ای کانفیگ‌ها"""
        from datetime import timedelta
        updated = 0
        for config in queryset:
            if config.expires_at:
                config.expires_at += timedelta(days=days)
                config.save()
                updated += 1
        return updated
    
    def bulk_activate_configs(self, request, queryset):
        """فعال‌سازی دسته‌ای کانفیگ‌ها"""
        return queryset.update(is_active=True)
    
    def bulk_deactivate_configs(self, request, queryset):
        """غیرفعال‌سازی دسته‌ای کانفیگ‌ها"""
        return queryset.update(is_active=False)
    
    def get_expiring_configs(self, days=7):
        """دریافت کانفیگ‌های در حال انقضا"""
        from xui_servers.models import UserConfig
        from datetime import timedelta
        
        future_date = timezone.now() + timedelta(days=days)
        return UserConfig.objects.filter(
            expires_at__gte=timezone.now(),
            expires_at__lte=future_date,
            is_active=True
        )
    
    def get_expired_configs(self):
        """دریافت کانفیگ‌های منقضی شده"""
        from xui_servers.models import UserConfig
        
        return UserConfig.objects.filter(
            expires_at__lt=timezone.now(),
            is_active=True
        )
    
    def get_user_summary(self, user):
        """دریافت خلاصه اطلاعات کاربر"""
        from xui_servers.models import UserConfig
        from order.models import OrderUserModel, PayMentModel
        from conf.models import TrialConfigModel
        
        summary = {
            'total_configs': UserConfig.objects.filter(user=user).count(),
            'active_configs': UserConfig.objects.filter(user=user, is_active=True).count(),
            'expired_configs': UserConfig.objects.filter(
                user=user, 
                expires_at__lt=timezone.now()
            ).count(),
            'total_orders': OrderUserModel.objects.filter(user=user).count(),
            'active_orders': OrderUserModel.objects.filter(user=user, is_active=True).count(),
            'total_payments': PayMentModel.objects.filter(user=user).count(),
            'approved_payments': PayMentModel.objects.filter(
                user=user, is_active=True, rejected=False
            ).count(),
            'has_trial': TrialConfigModel.objects.filter(user=user).exists(),
        }
        return summary


class AdvancedFiltersMixin:
    """کلاس میکسین برای فیلترهای پیشرفته"""
    
    def get_date_range_filter(self, request, field_name):
        """فیلتر بازه زمانی"""
        from django.contrib.admin import SimpleListFilter
        
        class DateRangeFilter(SimpleListFilter):
            title = f'فیلتر {field_name}'
            parameter_name = f'{field_name}_range'
            
            def lookups(self, request, model_admin):
                return (
                    ('today', 'امروز'),
                    ('yesterday', 'دیروز'),
                    ('this_week', 'این هفته'),
                    ('this_month', 'این ماه'),
                    ('last_month', 'ماه گذشته'),
                    ('last_7_days', '7 روز گذشته'),
                    ('last_30_days', '30 روز گذشته'),
                )
            
            def queryset(self, request, queryset):
                if self.value():
                    now = timezone.now()
                    if self.value() == 'today':
                        return queryset.filter(**{f'{field_name}__date': now.date()})
                    elif self.value() == 'yesterday':
                        yesterday = now - timedelta(days=1)
                        return queryset.filter(**{f'{field_name}__date': yesterday.date()})
                    elif self.value() == 'this_week':
                        return queryset.filter(**{f'{field_name}__week': now.isocalendar()[1]})
                    elif self.value() == 'this_month':
                        return queryset.filter(**{f'{field_name}__month': now.month})
                    elif self.value() == 'last_month':
                        last_month = now - timedelta(days=30)
                        return queryset.filter(**{f'{field_name}__month': last_month.month})
                    elif self.value() == 'last_7_days':
                        week_ago = now - timedelta(days=7)
                        return queryset.filter(**{f'{field_name}__gte': week_ago})
                    elif self.value() == 'last_30_days':
                        month_ago = now - timedelta(days=30)
                        return queryset.filter(**{f'{field_name}__gte': month_ago})
                return queryset
        
        return DateRangeFilter


class ExportMixin:
    """کلاس میکسین برای صادرات داده"""
    
    def export_to_csv(self, request, queryset):
        """صادرات به CSV"""
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="export.csv"'
        
        writer = csv.writer(response)
        
        # نوشتن هدر
        if queryset:
            field_names = [field.name for field in queryset.model._meta.fields]
            writer.writerow(field_names)
            
            # نوشتن داده‌ها
            for obj in queryset:
                row = []
                for field_name in field_names:
                    value = getattr(obj, field_name)
                    if hasattr(value, 'strftime'):  # برای فیلدهای تاریخ
                        value = value.strftime('%Y-%m-%d %H:%M:%S')
                    row.append(str(value))
                writer.writerow(row)
        
        return response
    
    def export_to_json(self, request, queryset):
        """صادرات به JSON"""
        from django.http import JsonResponse
        from django.core.serializers import serialize
        
        data = serialize('json', queryset)
        return JsonResponse({'data': data}, safe=False)


class NotificationMixin:
    """کلاس میکسین برای اعلان‌ها"""
    
    def send_notification(self, message, level='info'):
        """ارسال اعلان"""
        from django.contrib import messages
        
        if level == 'success':
            messages.success(self.request, message)
        elif level == 'error':
            messages.error(self.request, message)
        elif level == 'warning':
            messages.warning(self.request, message)
        else:
            messages.info(self.request, message)
    
    def log_action(self, action, user, details=None):
        """ثبت لاگ اکشن"""
        logger.info(f"Admin action: {action} by user {user} - Details: {details}") 