#!/usr/bin/env python3
"""
بررسی وضعیت سرویس‌ها
"""

import subprocess
import requests

def check_service(service_name, description):
    """بررسی سرویس"""
    print(f"🔧 {description}")
    result = subprocess.run(f"systemctl is-active {service_name}", shell=True, capture_output=True, text=True)
    if result.returncode == 0 and result.stdout.strip() == "active":
        print(f"✅ {description}: فعال")
        return True
    else:
        print(f"❌ {description}: غیرفعال")
        return False

def check_port(port, description):
    """بررسی پورت"""
    print(f"🔧 {description}")
    result = subprocess.run(f"ss -tlnp | grep :{port}", shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"✅ {description}: باز")
        return True
    else:
        print(f"❌ {description}: بسته")
        return False

def main():
    print("�� بررسی وضعیت سرویس‌ها")
    print("=" * 40)
    
    # بررسی سرویس‌ها
    services = [
        ("django-vpn", "Django VPN Service"),
        ("nginx", "Nginx"),
        ("redis-server", "Redis"),
        ("postgresql", "PostgreSQL")
    ]
    
    active_services = 0
    for service, desc in services:
        if check_service(service, desc):
            active_services += 1
    
    print(f"\n📊 سرویس‌های فعال: {active_services}/{len(services)}")
    
    # بررسی پورت‌ها
    ports = [
        (80, "HTTP (Nginx)"),
        (8000, "Django"),
        (54321, "X-UI Panel"),
        (6379, "Redis"),
        (5432, "PostgreSQL")
    ]
    
    open_ports = 0
    for port, desc in ports:
        if check_port(port, desc):
            open_ports += 1
    
    print(f"\n📊 پورت‌های باز: {open_ports}/{len(ports)}")
    
    print("\n�� بررسی کامل شد!")

if __name__ == "__main__":
    main()
