#!/usr/bin/env python3
"""
به‌روزرسانی سرویس X-UI
"""

def update_services_file():
    """به‌روزرسانی فایل services.py"""
    
    # خواندن فایل
    with open('xui_servers/services.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # جایگزینی endpoint ها
    old_endpoints = '''            # تست endpoint های مختلف برای ایجاد inbound
            add_endpoints = [
                "/panel/api/inbounds/add",
                "/panel/inbounds/add",
                "/api/inbounds/add",
                "/inbounds/add",
                "/api/inbound/add", 
                "/inbound/add"
            ]'''
    
    new_endpoints = '''            # استفاده از endpoint صحیح
            add_endpoints = ["/panel/api/inbounds/add"]'''
    
    content = content.replace(old_endpoints, new_endpoints)
    
    # ذخیره فایل
    with open('xui_servers/services.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ فایل services.py به‌روزرسانی شد")

if __name__ == "__main__":
    update_services_file()
