from django.contrib import admin
from .models import ActivityLog

@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'description', 'ip_address', 'timestamp']
    list_filter = ['action', 'timestamp']
    search_fields = ['user__username', 'description']
    date_hierarchy = 'timestamp'
    readonly_fields = ['user', 'action', 'description', 'ip_address', 'user_agent', 'timestamp', 'object_id', 'content_type', 'url', 'method']