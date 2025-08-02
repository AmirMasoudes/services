#!/usr/bin/env python3
"""
اصلاح indentation در فایل services.py
"""

def fix_indentation():
    """اصلاح indentation"""
    
    # خواندن فایل
    with open('xui_servers/services.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # جایگزینی کامل بخش endpoint ها
    old_section = '''            # تست endpoint های مختلف برای ایجاد inbound
            add_endpoints = [
                "/panel/api/inbounds/add",
                "/panel/inbounds/add",
                "/api/inbounds/add",
                "/inbounds/add",
                "/api/inbound/add", 
                "/inbound/add"
            ]'''
    
    new_section = '''            # استفاده از endpoint صحیح
            add_endpoints = ["/panel/api/inbounds/add"]'''
    
    content = content.replace(old_section, new_section)
    
    # ذخیره فایل
    with open('xui_servers/services.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Indentation اصلاح شد")

if __name__ == "__main__":
    fix_indentation()
