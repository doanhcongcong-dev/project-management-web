from django.urls import path
from . import views

app_name = 'tasks'

urlpatterns = [
    path('', views.list_view, name='list'),
    path('my-tasks/', views.my_tasks, name='my_tasks'),
    path('create/', views.create_view, name='create'),
    path('<int:pk>/', views.detail_view, name='detail'),
    path('<int:pk>/edit/', views.edit_view, name='edit'),
    path('<int:pk>/delete/', views.delete_view, name='delete'),
    path('<int:pk>/update-progress/', views.update_progress, name='update_progress'),
]