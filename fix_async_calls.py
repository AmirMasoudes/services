#!/usr/bin/env python3
"""
اسکریپت برای تبدیل فراخوانی‌های async به sync
این اسکریپت به شما کمک می‌کند تا کدهای موجود را به‌روزرسانی کنید
"""

import os
import re
import sys

def find_async_calls(directory="."):
    """یافتن فراخوانی‌های async در فایل‌ها"""
    print("🔍 جستجو برای فراخوانی‌های async...")
    
    async_patterns = [
        r'await\s+client_manager\.create_trial_config_async\(',
        r'await\s+client_manager\.create_user_config_async\(',
        r'client_manager\.create_trial_config_async\(',
        r'client_manager\.create_user_config_async\(',
    ]
    
    files_to_update = []
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    for pattern in async_patterns:
                        if re.search(pattern, content):
                            files_to_update.append((file_path, pattern))
                            break
                            
                except Exception as e:
                    print(f"❌ خطا در خواندن فایل {file_path}: {e}")
    
    return files_to_update

def update_file(file_path, old_pattern, new_pattern):
    """به‌روزرسانی فایل با جایگزینی الگو"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # جایگزینی الگوها
        updated_content = content
        
        # جایگزینی create_trial_config_async
        updated_content = re.sub(
            r'await\s+client_manager\.create_trial_config_async\(',
            'client_manager.create_trial_config_sync(',
            updated_content
        )
        
        updated_content = re.sub(
            r'client_manager\.create_trial_config_async\(',
            'client_manager.create_trial_config_sync(',
            updated_content
        )
        
        # جایگزینی create_user_config_async
        updated_content = re.sub(
            r'await\s+client_manager\.create_user_config_async\(',
            'client_manager.create_user_config_sync(',
            updated_content
        )
        
        updated_content = re.sub(
            r'client_manager\.create_user_config_async\(',
            'client_manager.create_user_config_sync(',
            updated_content
        )
        
        # ذخیره فایل
        if updated_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            print(f"✅ فایل {file_path} به‌روزرسانی شد")
            return True
        else:
            print(f"ℹ️ فایل {file_path} تغییری نداشت")
            return False
            
    except Exception as e:
        print(f"❌ خطا در به‌روزرسانی فایل {file_path}: {e}")
        return False

def show_usage_examples():
    """نمایش مثال‌های استفاده"""
    print("\n📚 مثال‌های استفاده:")
    print("=" * 50)
    
    print("\n🔧 قبل از به‌روزرسانی (async):")
    print("""
# در Telegram Bot
user_config = await client_manager.create_trial_config_async(user, inbound)

# در Django View
user_config = await client_manager.create_user_config_async(user, plan, inbound)
    """)
    
    print("\n✅ بعد از به‌روزرسانی (sync):")
    print("""
# در Telegram Bot
user_config = client_manager.create_trial_config_sync(user, inbound)

# در Django View
user_config = client_manager.create_user_config_sync(user, plan, inbound)
    """)
    
    print("\n⚠️ نکات مهم:")
    print("1. حذف await از فراخوانی‌ها")
    print("2. تغییر نام متدها از _async به _sync")
    print("3. اطمینان از اینکه در context sync هستید")

def main():
    """تابع اصلی"""
    print("🔧 اسکریپت تبدیل async به sync")
    print("=" * 40)
    
    # یافتن فایل‌های نیازمند به‌روزرسانی
    files_to_update = find_async_calls()
    
    if not files_to_update:
        print("✅ هیچ فراخوانی async یافت نشد!")
        return
    
    print(f"\n📁 {len(files_to_update)} فایل نیازمند به‌روزرسانی یافت شد:")
    for file_path, pattern in files_to_update:
        print(f"   - {file_path}")
    
    # سوال از کاربر
    response = input("\n❓ آیا می‌خواهید این فایل‌ها به‌روزرسانی شوند؟ (y/n): ")
    
    if response.lower() in ['y', 'yes', 'بله']:
        print("\n🔄 شروع به‌روزرسانی...")
        
        updated_count = 0
        for file_path, pattern in files_to_update:
            if update_file(file_path, pattern, ""):
                updated_count += 1
        
        print(f"\n✅ {updated_count} فایل به‌روزرسانی شد")
        
        if updated_count > 0:
            print("\n🎉 به‌روزرسانی با موفقیت انجام شد!")
            print("حالا می‌توانید کدهای خود را بدون مشکل async اجرا کنید")
    
    else:
        print("\nℹ️ به‌روزرسانی لغو شد")
    
    # نمایش مثال‌ها
    show_usage_examples()

if __name__ == "__main__":
    main()
