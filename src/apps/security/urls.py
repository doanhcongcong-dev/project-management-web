from django.urls import path
from . import views

app_name = 'security'

urlpatterns = [
    path('logs/', views.log_list, name='logs'),
    path('2fa/setup/', views.setup_2fa, name='2fa_setup'),
    path('2fa/verify/', views.verify_2fa, name='2fa_verify'),
    path('2fa/disable/', views.disable_2fa, name='2fa_disable'),
    path('encrypt-demo/', views.encrypt_demo, name='encrypt_demo'),
]