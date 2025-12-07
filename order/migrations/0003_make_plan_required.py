# Generated migration to make plan field required

import django.db.models.deletion
from django.db import migrations, models


def ensure_all_orders_have_plan(apps, schema_editor):
    """Ensure all orders have a plan before making it required"""
    OrderUserModel = apps.get_model('order', 'OrderUserModel')
    ConfingPlansModel = apps.get_model('plan', 'ConfingPlansModel')
    
    # Get default plan (first active plan or first plan)
    default_plan = ConfingPlansModel.objects.filter(is_active=True).first()
    if not default_plan:
        default_plan = ConfingPlansModel.objects.first()
    
    # If no plans exist, skip the update (migration will handle it)
    
    if default_plan:
        # Update any orders without a plan
        OrderUserModel.objects.filter(plan__isnull=True).update(plan=default_plan)


class Migration(migrations.Migration):

    dependencies = [
        ('plan', '0001_initial'),
        ('order', '0002_rename_plans_to_plan_and_add_new_fields'),
    ]

    operations = [
        # Ensure all orders have a plan
        migrations.RunPython(
            code=ensure_all_orders_have_plan,
            reverse_code=migrations.RunPython.noop,
        ),
        # Make plan field required (non-nullable)
        migrations.AlterField(
            model_name='orderusermodel',
            name='plan',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='orders',
                to='plan.confingplansmodel'
            ),
        ),
    ]

