from django.http import HttpResponse
from django.shortcuts import render

def home(request):
    return HttpResponse("""
    <html>
    <head>
        <title>VPN Service</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .container { max-width: 800px; margin: 0 auto; }
            .status { padding: 10px; margin: 10px 0; border-radius: 5px; }
            .success { background-color: #d4edda; color: #155724; }
            .info { background-color: #d1ecf1; color: #0c5460; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 VPN Service</h1>
            <div class="status success">
                ✅ سیستم فعال و آماده استفاده است
            </div>
            <div class="status info">
                📊 وضعیت سرویس‌ها:
                <ul>
                    <li>Django: فعال</li>
                    <li>X-UI: فعال</li>
                    <li>User Bot: فعال</li>
                    <li>Admin Bot: فعال</li>
                </ul>
            </div>
            <div class="status info">
                🔗 لینک‌های مهم:
                <ul>
                    <li>X-UI Panel: <a href="http://38.54.105.181:44">http://38.54.105.181:44</a></li>
                    <li>Django Admin: <a href="/admin">Admin Panel</a></li>
                </ul>
            </div>
        </div>
    </body>
    </html>
    """)
