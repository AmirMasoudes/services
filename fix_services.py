#!/usr/bin/env python3
"""
اصلاح کامل فایل services.py
"""

def fix_services():
    """اصلاح فایل services.py"""
    
    # خواندن فایل
    with open('xui_servers/services.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # پیدا کردن و اصلاح خط endpoint ها
    for i, line in enumerate(lines):
        if 'add_endpoints = [' in line:
            # حذف خطوط قدیمی
            lines[i] = '            add_endpoints = ["/panel/api/inbounds/add"]\n'
            # حذف خطوط بعدی که آرایه هستند
            j = i + 1
            while j < len(lines) and ('"/panel/' in lines[j] or '"/api/' in lines[j] or '"/inbound' in lines[j] or ']' in lines[j]):
                lines[j] = ''
                j += 1
            break
    
    # ذخیره فایل
    with open('xui_servers/services.py', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print("✅ فایل services.py اصلاح شد")

if __name__ == "__main__":
    fix_services()
