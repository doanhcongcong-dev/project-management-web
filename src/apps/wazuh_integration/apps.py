from django.apps import AppConfig

class WazuhIntegrationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.wazuh_integration'
    verbose_name = 'Tích hợp Wazuh'