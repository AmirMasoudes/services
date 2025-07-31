from django.urls import path
from . import views

app_name = 'plan'

urlpatterns = [
    path('plans/', views.PlanListView.as_view(), name='plan-list'),
    path('plans/<uuid:pk>/', views.PlanDetailView.as_view(), name='plan-detail'),
] 