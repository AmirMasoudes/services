import os

from celery import Celery

# تنظیم ماژول تنظیمات جنگو برای celery
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("config")

# خواندن تنظیمات celery از تنظیمات جنگو
app.config_from_object("django.conf:settings", namespace="CELERY")

# کشف خودکار فایل‌های tasks.py در اپ‌ها
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")


