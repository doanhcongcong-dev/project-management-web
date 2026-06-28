from django.urls import path
from . import views

app_name = 'wazuh_integration'

urlpatterns = [
    path('', views.alert_list, name='alert_list'),
    path('<int:pk>/', views.alert_detail, name='alert_detail'),
    path('<int:pk>/acknowledge/', views.acknowledge_alert, name='acknowledge_alert'),
    path('sync/', views.sync_alerts_view, name='sync_alerts'),
]