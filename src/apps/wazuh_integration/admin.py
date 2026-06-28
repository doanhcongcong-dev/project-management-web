from django.contrib import admin
from .models import WazuhAlert

@admin.register(WazuhAlert)
class WazuhAlertAdmin(admin.ModelAdmin):
    list_display = ['alert_id', 'level', 'rule_description', 'timestamp', 'is_acknowledged']
    list_filter = ['level', 'is_acknowledged']
    search_fields = ['rule_description', 'source_ip', 'agent_name']
    date_hierarchy = 'timestamp'
    readonly_fields = ['alert_id', 'timestamp', 'raw_data']