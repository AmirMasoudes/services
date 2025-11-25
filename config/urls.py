from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    
    # API URLs
    path('api/accounts/', include('accounts.urls')),
    path('api/orders/', include('order.urls')),
    path('api/plans/', include('plan.urls')),
    path('api/configs/', include('conf.urls')),
    path('api/messages/', include('chat_messages.urls')),
    
    path('', views.home, name='home'),
]

# Serving static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
