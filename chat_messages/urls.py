from django.urls import path
from . import views

app_name = 'messages'

urlpatterns = [
    path('directories/', views.DirectoryListView.as_view(), name='directory-list'),
    path('directories/<uuid:pk>/', views.DirectoryDetailView.as_view(), name='directory-detail'),
    path('messages/', views.MessageListView.as_view(), name='message-list'),
    path('messages/<uuid:pk>/', views.MessageDetailView.as_view(), name='message-detail'),
] 