from django.contrib import admin
from .models import Milestone

@admin.register(Milestone)
class MilestoneAdmin(admin.ModelAdmin):
    list_display = ['name', 'project', 'due_date', 'status', 'get_progress']
    list_filter = ['status', 'project', 'due_date']
    search_fields = ['name', 'description']
    date_hierarchy = 'due_date'
    raw_id_fields = ['project', 'created_by']
    filter_horizontal = ['tasks']

    def get_progress(self, obj):
        return f"{obj.get_progress()}%"
    get_progress.short_description = 'Tiến độ'