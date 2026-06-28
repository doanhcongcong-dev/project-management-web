from django.urls import path
from . import views

app_name = 'activity_log'

urlpatterns = [
    path('', views.list_view, name='list'),
    path('<int:pk>/', views.detail_view, name='detail'),
]