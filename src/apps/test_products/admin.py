from django.contrib import admin
from .models import TestProduct

@admin.register(TestProduct)
class TestProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'version', 'project', 'result', 'tester', 'test_date']
    list_filter = ['result', 'project', 'tester']
    search_fields = ['name', 'version', 'notes']
    date_hierarchy = 'test_date'
    raw_id_fields = ['project', 'tester']