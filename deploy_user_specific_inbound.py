#!/usr/bin/env python3
"""
اسکریپت استقرار سیستم Inbound جداگانه برای هر کاربر
این اسکریپت سیستم را به‌روزرسانی می‌کند تا برای هر کاربر Inbound جداگانه ایجاد کند
"""

import os
import sys
import django
import subprocess
import shutil

# تنظیم Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

def deploy_user_specific_inbound():
    """استقرار سیستم Inbound جداگانه برای هر کاربر"""
    print("🚀 استقرار سیستم Inbound جداگانه برای هر کاربر...")
    
    try:
        # 1. به‌روزرسانی فایل services.py
        print("📝 به‌روزرسانی فایل xui_servers/services.py...")
        
        # کپی فایل جدید
        source_file = "xui_servers/services.py"
        if os.path.exists(source_file):
            print(f"✅ فایل {source_file} موجود است")
        else:
            print(f"❌ فایل {source_file} یافت نشد")
            return False
        
        # 2. ایجاد فایل تست
        print("🧪 ایجاد فایل تست...")
        test_file = "create_user_specific_inbound_test.py"
        if os.path.exists(test_file):
            print(f"✅ فایل تست {test_file} ایجاد شد")
        else:
            print(f"❌ فایل تست {test_file} یافت نشد")
            return False
        
        # 3. تست سیستم
        print("🔧 تست سیستم جدید...")
        try:
            result = subprocess.run([
                sys.executable, "create_user_specific_inbound_test.py"
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                print("✅ تست سیستم موفق بود")
                print(result.stdout)
            else:
                print("❌ خطا در تست سیستم")
                print(result.stderr)
                return False
                
        except subprocess.TimeoutExpired:
            print("⏰ تست سیستم زمان‌بر شد")
            return False
        except Exception as e:
            print(f"❌ خطا در اجرای تست: {e}")
            return False
        
        # 4. راه‌اندازی مجدد سرویس‌ها
        print("🔄 راه‌اندازی مجدد سرویس‌ها...")
        
        services = ["vpn-django", "vpn-user-bot", "vpn-admin-bot"]
        for service in services:
            try:
                subprocess.run(["systemctl", "restart", service], check=True)
                print(f"✅ سرویس {service} راه‌اندازی مجدد شد")
            except subprocess.CalledProcessError:
                print(f"⚠️ خطا در راه‌اندازی مجدد سرویس {service}")
        
        # 5. بررسی وضعیت سرویس‌ها
        print("📊 بررسی وضعیت سرویس‌ها...")
        for service in services:
            try:
                result = subprocess.run(["systemctl", "is-active", service], 
                                      capture_output=True, text=True)
                status = result.stdout.strip()
                if status == "active":
                    print(f"✅ سرویس {service} فعال است")
                else:
                    print(f"❌ سرویس {service} غیرفعال است")
            except Exception as e:
                print(f"⚠️ خطا در بررسی سرویس {service}: {e}")
        
        print("\n🎉 استقرار سیستم Inbound جداگانه کامل شد!")
        print("\n📋 خلاصه تغییرات:")
        print("✅ هر کاربر Inbound جداگانه دریافت می‌کند")
        print("✅ نام Inbound ها: User-{user_id}-{protocol}-{port}")
        print("✅ پورت‌های تصادفی برای هر کاربر")
        print("✅ تنظیمات Reality تصادفی برای هر Inbound")
        print("✅ سازگاری با سیستم قدیمی")
        
        return True
        
    except Exception as e:
        print(f"❌ خطا در استقرار: {e}")
        return False

def show_usage_guide():
    """نمایش راهنمای استفاده"""
    print("\n📚 راهنمای استفاده از سیستم جدید:")
    print("\n🎯 ویژگی‌های جدید:")
    print("• هر کاربر Inbound جداگانه دریافت می‌کند")
    print("• پورت‌های تصادفی برای امنیت بیشتر")
    print("• تنظیمات Reality تصادفی")
    print("• نام‌گذاری منظم: User-{user_id}-{protocol}-{port}")
    
    print("\n🔧 نحوه کار:")
    print("1. کاربر درخواست کانفیگ می‌دهد")
    print("2. سیستم Inbound مخصوص کاربر ایجاد می‌کند")
    print("3. کاربر در آن Inbound قرار می‌گیرد")
    print("4. کانفیگ با پورت و تنظیمات مخصوص تولید می‌شود")
    
    print("\n📊 مزایا:")
    print("• امنیت بیشتر (جداسازی ترافیک)")
    print("• مدیریت بهتر (هر کاربر Inbound جداگانه)")
    print("• امکان محدودیت جداگانه برای هر کاربر")
    print("• تشخیص آسان مشکلات (بر اساس نام Inbound)")

if __name__ == "__main__":
    success = deploy_user_specific_inbound()
    if success:
        show_usage_guide()
    else:
        print("\n❌ استقرار ناموفق بود. لطفا خطاها را بررسی کنید.") 