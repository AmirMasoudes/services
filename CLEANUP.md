# Cleanup Report

## Files Removed/Archived

### Critical Removals

#### 1. `db.sqlite3`
- **Status:** ✅ Already in `.gitignore`
- **Action Required:** Remove from git history if committed
- **Command:**
  ```bash
  git rm --cached db.sqlite3
  git commit -m "chore: remove db.sqlite3 from repository"
  ```

#### 2. `config.env`
- **Status:** ✅ Already in `.gitignore`
- **Action Required:** 
  - Remove from git history if committed
  - Create `.env.example` template (already documented)
  - Rotate all secrets if file was committed
- **Command:**
  ```bash
  git rm --cached config.env
  git commit -m "chore: remove config.env from repository"
  ```

### Files to Review

#### 3. Temporary Fix Scripts
- **Files:** `fix_*.py`, `*_fix.py`, `*_fix_*.py`
- **Status:** ⚠️ Should be reviewed and removed if no longer needed
- **Action:** Review each file, remove if obsolete

#### 4. Duplicate API Files
- **Files:** 
  - `xui_servers/sanaei_api.py` (X-UI specific)
  - `xui_servers/enhanced_api_models.py` (Enhanced X-UI)
  - `xui_servers/sui_client.py` (S-UI client - NEW)
- **Status:** ⚠️ Consider consolidating or clearly documenting purpose
- **Action:** Keep all for now, but document which to use when

#### 5. Unused Migration Files
- **Status:** ⚠️ Review migrations, don't delete without backup
- **Action:** Keep all migrations, they're part of history

### Files to Keep

#### 6. Documentation Files
- **Keep:** All `.md` files
- **Reason:** Important documentation

#### 7. Service Files
- **Keep:** `services/*.service`
- **Reason:** Systemd service definitions

#### 8. Setup Scripts
- **Keep:** `setup_*.sh`, `install_*.sh`
- **Reason:** Deployment scripts

---

## Git History Cleanup

### Remove Sensitive Data from History

If `config.env` or `db.sqlite3` were committed:

```bash
# Install git-filter-repo
pip install git-filter-repo

# Remove config.env from history
git filter-repo --path config.env --invert-paths

# Remove db.sqlite3 from history
git filter-repo --path db.sqlite3 --invert-paths

# Force push (WARNING: This rewrites history)
git push origin --force --all
```

**⚠️ WARNING:** Only do this if you're sure no one else has cloned the repo, or coordinate with your team.

---

## Code Cleanup

### 1. Remove Commented Code

Search for large blocks of commented code:

```bash
# Find files with many commented lines
grep -r "^[[:space:]]*#" --include="*.py" . | wc -l
```

Review and remove unnecessary comments.

### 2. Remove Unused Imports

```bash
# Use autoflake or ruff
ruff check --select F401 .
```

### 3. Remove Debug Print Statements

```bash
# Find print statements
grep -r "print(" --include="*.py" .

# Replace with proper logging
```

---

## Database Cleanup

### 1. Remove Test Data

```python
# In Django shell
python manage.py shell

from accounts.models import UsersModel
from order.models import OrderUserModel

# Remove test users (be careful!)
# UsersModel.objects.filter(username_tel__startswith='test_').delete()
```

### 2. Clean Up Orphaned Records

```python
# Find orphaned UserConfigs
from xui_servers.models import UserConfig, XUIServer

# Configs with deleted servers
UserConfig.objects.filter(server__isnull=True).count()

# Configs with deleted users
UserConfig.objects.filter(user__isnull=True).count()
```

---

## Log Cleanup

### 1. Rotate Logs

```bash
# Use logrotate or similar
logrotate -f /etc/logrotate.d/django
```

### 2. Remove Old Logs

```bash
# Remove logs older than 30 days
find logs/ -name "*.log" -mtime +30 -delete
```

---

## Media Cleanup

### 1. Remove Old Payment Images

```python
# In Django shell
from order.models import PayMentModel
from django.utils import timezone
from datetime import timedelta

# Remove payment images older than 1 year
old_payments = PayMentModel.objects.filter(
    created_at__lt=timezone.now() - timedelta(days=365)
)
for payment in old_payments:
    if payment.images:
        payment.images.delete()
```

---

## Recommendations

### Immediate Actions

1. ✅ Verify `.gitignore` is up to date
2. ✅ Remove `db.sqlite3` from repository if present
3. ✅ Remove `config.env` from repository if present
4. ✅ Create `.env.example` template
5. ⚠️ Review and remove temporary fix scripts
6. ⚠️ Clean up commented code

### Future Actions

1. Set up log rotation
2. Implement automated cleanup tasks
3. Regular database maintenance
4. Archive old media files
5. Monitor disk usage

---

## Automated Cleanup Tasks

Consider adding Celery tasks for automated cleanup:

```python
@shared_task
def cleanup_old_logs():
    """Remove logs older than 30 days"""
    pass

@shared_task
def cleanup_old_media():
    """Remove old payment images"""
    pass

@shared_task
def cleanup_orphaned_records():
    """Remove orphaned database records"""
    pass
```

---

## Summary

- **Files Removed:** 0 (all handled by .gitignore)
- **Files to Review:** 5 categories
- **Git History:** May need cleanup if secrets were committed
- **Code Cleanup:** Remove commented code, unused imports
- **Database Cleanup:** Remove test data, orphaned records
- **Log Cleanup:** Implement rotation

All critical files are already in `.gitignore`. Focus on:
1. Removing secrets from git history (if committed)
2. Cleaning up temporary scripts
3. Removing commented code
4. Setting up automated cleanup

