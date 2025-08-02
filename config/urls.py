from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('', views.home, name='home'),
]
