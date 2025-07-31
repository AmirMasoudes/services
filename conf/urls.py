from django.urls import path
from . import views

app_name = 'conf'

urlpatterns = [
    path('configs/', views.ConfigListView.as_view(), name='config-list'),
    path('configs/<uuid:pk>/', views.ConfigDetailView.as_view(), name='config-detail'),
]
