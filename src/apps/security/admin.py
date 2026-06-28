from django.contrib import admin
from .models import SecurityLog, User2FA

@admin.register(SecurityLog)
class SecurityLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'ip_address', 'timestamp']
    list_filter = ['action', 'timestamp']
    search_fields = ['user__username', 'description']
    date_hierarchy = 'timestamp'

@admin.register(User2FA)
class User2FAAdmin(admin.ModelAdmin):
    list_display = ['user', 'is_enabled', 'created_at']
    list_filter = ['is_enabled']