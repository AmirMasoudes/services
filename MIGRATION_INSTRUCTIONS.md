# Migration Instructions

## Critical: Read Before Migrating

⚠️ **BACKUP YOUR DATABASE BEFORE RUNNING MIGRATIONS**

```bash
# SQLite
cp db.sqlite3 db.sqlite3.backup

# PostgreSQL
pg_dump database_name > backup.sql
```

---

## Step-by-Step Migration

### 1. Review Changes

The following models have been modified:

#### `order/models.py`
- **BREAKING:** `plans` field changed from `OneToOneField` to `ForeignKey`
- **NEW:** `status` field with choices
- **NEW:** `order_number` field (auto-generated)
- **NEW:** Payment tracking fields
- **NEW:** Indexes added

#### `xui_servers/models.py`
- **NEW:** `XUIServer` - Added health check, sync, server_type fields
- **NEW:** `XUIInbound` - Added stream_settings, sniffing_settings, indexes
- **NEW:** `XUIClient` - Added sync tracking fields, indexes
- **NEW:** `UserConfig` - Added status, subscription_url, sync fields, indexes
- **NEW:** `AuditLog` - New model for audit tracking

### 2. Create Migrations

```bash
python manage.py makemigrations order
python manage.py makemigrations xui_servers
```

### 3. Review Generated Migrations

```bash
# Review order migrations
cat order/migrations/XXXX_order_changes.py

# Review xui_servers migrations
cat xui_servers/migrations/XXXX_xui_changes.py
```

**Important:** Check that:
- Data migrations are included for existing data
- Default values are set correctly
- Index creation is included

### 4. Test Migrations (Development)

```bash
# On a copy of production data
python manage.py migrate --plan
python manage.py migrate --dry-run  # If supported
```

### 5. Apply Migrations

```bash
# Apply all migrations
python manage.py migrate

# Or apply specific app
python manage.py migrate order
python manage.py migrate xui_servers
```

### 6. Verify Migration

```bash
python manage.py shell
```

```python
from order.models import OrderUserModel
from xui_servers.models import UserConfig, AuditLog

# Check OrderUserModel
orders = OrderUserModel.objects.all()
print(f"Total orders: {orders.count()}")
for order in orders[:5]:
    print(f"Order: {order.order_number}, Status: {order.status}")

# Check UserConfig
configs = UserConfig.objects.all()
print(f"Total configs: {configs.count()}")
for config in configs[:5]:
    print(f"Config: {config.config_name}, Status: {config.status}, URL: {config.subscription_url}")

# Check AuditLog
logs = AuditLog.objects.all()
print(f"Total audit logs: {logs.count()}")
```

### 7. Data Migration (If Needed)

If you have existing data that needs migration:

```python
# In Django shell
from order.models import OrderUserModel
import uuid

# Generate order numbers for existing orders
for order in OrderUserModel.objects.filter(order_number__isnull=True):
    order.order_number = f"ORD-{uuid.uuid4().hex[:8].upper()}"
    order.save()

# Set default status for existing orders
OrderUserModel.objects.filter(status='').update(status='pending')

# Set default status for existing configs
from xui_servers.models import UserConfig
UserConfig.objects.filter(status='').update(status='active' if UserConfig.is_active else 'pending')
```

---

## Rollback Instructions

If migration fails:

### SQLite
```bash
# Restore backup
cp db.sqlite3.backup db.sqlite3

# Or manually rollback
python manage.py migrate order XXXX  # Previous migration number
python manage.py migrate xui_servers XXXX
```

### PostgreSQL
```bash
# Restore backup
psql database_name < backup.sql

# Or rollback migrations
python manage.py migrate order XXXX
python manage.py migrate xui_servers XXXX
```

---

## Post-Migration Tasks

### 1. Update Code References

Search for old field names:

```bash
# Find references to old 'plans' field (OneToOne)
grep -r "\.plans" --include="*.py" .

# Update to new 'plan' field (ForeignKey)
# Change: order.plans
# To: order.plan
```

### 2. Update Bot Code

Update bot handlers that use old field names:

```python
# Old
order.plans.name

# New
order.plan.name
```

### 3. Verify Functionality

1. Test order creation
2. Test subscription provisioning
3. Test admin bot commands
4. Test user bot commands
5. Check database queries

---

## Common Issues

### Issue: Migration fails with "column does not exist"

**Solution:** You may have existing migrations that conflict. Try:

```bash
python manage.py migrate --fake-initial
```

### Issue: "Cannot add foreign key constraint"

**Solution:** Ensure referenced tables exist:

```bash
python manage.py migrate accounts  # If UsersModel is in accounts
python manage.py migrate plan      # If ConfingPlansModel is in plan
```

### Issue: "Default value is invalid"

**Solution:** Check that default values match field types:

```python
# In migration file, ensure defaults are correct
status = models.CharField(default='pending', ...)  # Not ''
```

---

## Migration Checklist

- [ ] Database backed up
- [ ] Migrations created
- [ ] Migrations reviewed
- [ ] Tested on development
- [ ] Code references updated
- [ ] Migrations applied
- [ ] Data verified
- [ ] Functionality tested
- [ ] Rollback plan ready

---

## Support

If migration fails:
1. Check error message
2. Review migration file
3. Check database state
4. Restore from backup if needed
5. Contact development team

