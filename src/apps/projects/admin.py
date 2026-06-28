from django.contrib import admin
from .models import Project

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'status', 'start_date', 'end_date', 'manager', 'get_member_count']
    list_filter = ['status', 'start_date']
    search_fields = ['name', 'description']
    date_hierarchy = 'start_date'
    filter_horizontal = ['members']
    raw_id_fields = ['manager']

    def get_member_count(self, obj):
        return obj.members.count()
    get_member_count.short_description = 'Số thành viên'