from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('', views.list_view, name='list'),
    path('<int:pk>/', views.detail_view, name='detail'),
    path('<int:pk>/mark-read/', views.mark_as_read, name='mark_read'),
    path('mark-all-read/', views.mark_all_read, name='mark_all_read'),
    path('<int:pk>/delete/', views.delete_view, name='delete'),
    path('api/unread-count/', views.get_unread_count, name='api_unread_count'),
    path('api/latest/', views.get_latest_notifications, name='api_latest'),
]