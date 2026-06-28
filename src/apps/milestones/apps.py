from django.apps import AppConfig

class MilestonesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.milestones'
    verbose_name = 'Cột mốc'

    def ready(self):
        import apps.milestones.signals