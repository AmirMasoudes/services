#!/usr/bin/env python3
"""
تست اتصال با HTTP و HTTPS
"""

import requests
import urllib3
from urllib3.exceptions import InsecureRequestWarning

# غیرفعال کردن هشدارهای SSL
urllib3.disable_warnings(InsecureRequestWarning)

def test_connection(host, port, path, use_ssl=False):
    """تست اتصال با HTTP یا HTTPS"""
    protocol = "https" if use_ssl else "http"
    url = f"{protocol}://{host}:{port}{path}"
    
    print(f"\n🔗 تست اتصال به: {url}")
    
    try:
        response = requests.get(
            url,
            timeout=10,
            verify=False,  # برای HTTPS با self-signed certificate
            allow_redirects=True
        )
        
        print(f"✅ وضعیت: {response.status_code}")
        print(f"✅ هدرها: {dict(response.headers)}")
        print(f"✅ محتوا (اول 200 کاراکتر): {response.text[:200]}...")
        return True
        
    except requests.exceptions.SSLError as e:
        print(f"❌ خطای SSL: {e}")
        return False
    except requests.exceptions.ConnectionError as e:
        print(f"❌ خطای اتصال: {e}")
        return False
    except requests.exceptions.Timeout as e:
        print(f"❌ خطای timeout: {e}")
        return False
    except Exception as e:
        print(f"❌ خطای عمومی: {e}")
        return False

def main():
    """تست اصلی"""
    host = "time.amirprogrammer.ir"
    port = 50987
    path = "/YvIhWQ3Pt6cHGXegE4/"
    
    print("🚀 تست پروتکل‌های HTTP و HTTPS")
    print("=" * 50)
    
    # تست HTTP
    print("\n📡 تست HTTP...")
    http_result = test_connection(host, port, path, use_ssl=False)
    
    # تست HTTPS
    print("\n🔒 تست HTTPS...")
    https_result = test_connection(host, port, path, use_ssl=True)
    
    # نتایج
    print("\n" + "=" * 50)
    print("📊 نتایج نهایی:")
    print(f"   • HTTP: {'✅ موفق' if http_result else '❌ ناموفق'}")
    print(f"   • HTTPS: {'✅ موفق' if https_result else '❌ ناموفق'}")
    
    if https_result:
        print("\n🎉 سرور از HTTPS پشتیبانی می‌کند!")
        return "https"
    elif http_result:
        print("\n⚠️ سرور فقط از HTTP پشتیبانی می‌کند.")
        return "http"
    else:
        print("\n❌ هیچ پروتکلی کار نمی‌کند!")
        return None

if __name__ == "__main__":
    result = main()
