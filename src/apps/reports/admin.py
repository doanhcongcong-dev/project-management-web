from django.contrib import admin
from .models import ReportLog

@admin.register(ReportLog)
class ReportLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'report_type', 'exported_at']
    list_filter = ['report_type', 'exported_at']
    search_fields = ['user__username']