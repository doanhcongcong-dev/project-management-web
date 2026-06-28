from django.contrib import admin
from .models import Task

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'project', 'status', 'priority', 'due_date', 'assigned_to_list']
    list_filter = ['status', 'priority', 'project']
    search_fields = ['title', 'description']
    date_hierarchy = 'due_date'
    raw_id_fields = ['project', 'created_by']
    filter_horizontal = ['assigned_to']

    def assigned_to_list(self, obj):
        return ', '.join([user.username for user in obj.assigned_to.all()])
    assigned_to_list.short_description = 'Người được giao'