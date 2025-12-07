# Generated migration to fix plan field and add new fields

import django.db.models.deletion
from django.db import migrations, models
import django.utils.timezone


def migrate_plans_to_plan(apps, schema_editor):
    """Copy data from old plans field to new plan field"""
    OrderUserModel = apps.get_model('order', 'OrderUserModel')
    for order in OrderUserModel.objects.all():
        if hasattr(order, 'plans') and order.plans:
            order.plan = order.plans
            order.save(update_fields=['plan'])


def migrate_plan_to_plans(apps, schema_editor):
    """Reverse migration: copy from plan back to plans"""
    OrderUserModel = apps.get_model('order', 'OrderUserModel')
    for order in OrderUserModel.objects.all():
        if hasattr(order, 'plan') and order.plan:
            order.plans = order.plan
            order.save(update_fields=['plans'])


class Migration(migrations.Migration):

    dependencies = [
        ('plan', '0001_initial'),
        ('order', '0001_initial'),
    ]

    operations = [
        # Step 1: Add new plan field as nullable ForeignKey
        migrations.AddField(
            model_name='orderusermodel',
            name='plan',
            field=models.ForeignKey(
                null=True,
                blank=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='orders',
                to='plan.confingplansmodel'
            ),
        ),
        # Step 2: Copy data from plans to plan (if plans exists)
        migrations.RunPython(
            code=lambda apps, schema_editor: migrate_plans_to_plan(apps, schema_editor),
            reverse_code=lambda apps, schema_editor: migrate_plan_to_plans(apps, schema_editor),
        ),
        # Step 3: Remove old plans field
        migrations.RemoveField(
            model_name='orderusermodel',
            name='plans',
        ),
        # Step 4: Keep plan nullable for now - will be made required in next migration
        # Step 5: Fix start_plane_at and end_plane_at to allow null
        migrations.AlterField(
            model_name='orderusermodel',
            name='start_plane_at',
            field=models.DateTimeField(editable=False, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='orderusermodel',
            name='end_plane_at',
            field=models.DateTimeField(editable=False, null=True, blank=True),
        ),
        # Step 6: Add new fields
        migrations.AddField(
            model_name='orderusermodel',
            name='status',
            field=models.CharField(
                choices=[
                    ('pending', 'در انتظار پرداخت'),
                    ('paid', 'پرداخت شده'),
                    ('active', 'فعال'),
                    ('expired', 'منقضی شده'),
                    ('cancelled', 'لغو شده'),
                    ('refunded', 'بازگشت وجه'),
                ],
                db_index=True,
                default='pending',
                help_text='وضعیت سفارش',
                max_length=20
            ),
        ),
        migrations.AddField(
            model_name='orderusermodel',
            name='order_number',
            field=models.CharField(
                blank=True,
                db_index=True,
                help_text='شماره سفارش',
                max_length=50,
                null=True,
                unique=True
            ),
        ),
        migrations.AddField(
            model_name='orderusermodel',
            name='total_amount',
            field=models.PositiveIntegerField(default=0, help_text='مبلغ کل'),
        ),
        migrations.AddField(
            model_name='orderusermodel',
            name='paid_amount',
            field=models.PositiveIntegerField(default=0, help_text='مبلغ پرداخت شده'),
        ),
        migrations.AddField(
            model_name='orderusermodel',
            name='payment_method',
            field=models.CharField(
                blank=True,
                help_text='روش پرداخت',
                max_length=50,
                null=True
            ),
        ),
        migrations.AddField(
            model_name='orderusermodel',
            name='notes',
            field=models.TextField(blank=True, help_text='یادداشت\u200cها', null=True),
        ),
        migrations.AddField(
            model_name='orderusermodel',
            name='activated_at',
            field=models.DateTimeField(blank=True, help_text='زمان فعال\u200cسازی', null=True),
        ),
        migrations.AddField(
            model_name='orderusermodel',
            name='cancelled_at',
            field=models.DateTimeField(blank=True, help_text='زمان لغو', null=True),
        ),
        migrations.AddField(
            model_name='orderusermodel',
            name='cancelled_reason',
            field=models.TextField(blank=True, help_text='دلیل لغو', null=True),
        ),
        # Step 7: Add indexes
        migrations.AddIndex(
            model_name='orderusermodel',
            index=models.Index(fields=['user', 'status'], name='order_order_user_id_idx'),
        ),
        migrations.AddIndex(
            model_name='orderusermodel',
            index=models.Index(fields=['status', 'is_active'], name='order_order_status_i_idx'),
        ),
        migrations.AddIndex(
            model_name='orderusermodel',
            index=models.Index(fields=['order_number'], name='order_order_order_n_idx'),
        ),
        migrations.AddIndex(
            model_name='orderusermodel',
            index=models.Index(fields=['created_at'], name='order_order_created_idx'),
        ),
        # Step 8: Fix PayMentModel related_name
        migrations.AlterField(
            model_name='paymentmodel',
            name='order',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='payments',
                to='order.orderusermodel'
            ),
        ),
        migrations.AlterField(
            model_name='paymentmodel',
            name='user',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='user_payments',
                to='accounts.usersmodel'
            ),
        ),
        # Step 9: Add new fields to PayMentModel
        migrations.AddField(
            model_name='paymentmodel',
            name='status',
            field=models.CharField(
                choices=[
                    ('pending', 'در انتظار بررسی'),
                    ('approved', 'تایید شده'),
                    ('rejected', 'رد شده'),
                    ('refunded', 'بازگشت وجه'),
                ],
                db_index=True,
                default='pending',
                help_text='وضعیت پرداخت',
                max_length=20
            ),
        ),
        migrations.AddField(
            model_name='paymentmodel',
            name='amount',
            field=models.PositiveIntegerField(default=0, help_text='مبلغ پرداخت'),
        ),
        migrations.AddField(
            model_name='paymentmodel',
            name='payment_date',
            field=models.DateTimeField(blank=True, help_text='تاریخ پرداخت', null=True),
        ),
        migrations.AddField(
            model_name='paymentmodel',
            name='approved_at',
            field=models.DateTimeField(blank=True, help_text='زمان تایید', null=True),
        ),
        migrations.AddField(
            model_name='paymentmodel',
            name='approved_by',
            field=models.ForeignKey(
                blank=True,
                help_text='تایید کننده',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='approved_payments',
                to='accounts.usersmodel'
            ),
        ),
        migrations.AddField(
            model_name='paymentmodel',
            name='rejection_reason',
            field=models.TextField(blank=True, help_text='دلیل رد', null=True),
        ),
        migrations.AddField(
            model_name='paymentmodel',
            name='notes',
            field=models.TextField(blank=True, help_text='یادداشت\u200cها', null=True),
        ),
        # Step 10: Add indexes to PayMentModel
        migrations.AddIndex(
            model_name='paymentmodel',
            index=models.Index(fields=['user', 'status'], name='order_payme_user_id_idx'),
        ),
        migrations.AddIndex(
            model_name='paymentmodel',
            index=models.Index(fields=['order', 'status'], name='order_payme_order_id_idx'),
        ),
        migrations.AddIndex(
            model_name='paymentmodel',
            index=models.Index(fields=['code_pay'], name='order_payme_code_pa_idx'),
        ),
        migrations.AddIndex(
            model_name='paymentmodel',
            index=models.Index(fields=['status', 'created_at'], name='order_payme_status__idx'),
        ),
    ]

