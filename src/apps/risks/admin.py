from django.contrib import admin
from .models import RiskCategory, Risk, RiskHistory

@admin.register(RiskCategory)
class RiskCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']

@admin.register(Risk)
class RiskAdmin(admin.ModelAdmin):
    list_display = ['title', 'project', 'category', 'risk_score', 'status', 'assigned_to', 'created_at']
    list_filter = ['status', 'category', 'project']
    search_fields = ['title', 'description']
    date_hierarchy = 'created_at'
    raw_id_fields = ['project', 'assigned_to', 'created_by']
    readonly_fields = ['risk_score']

@admin.register(RiskHistory)
class RiskHistoryAdmin(admin.ModelAdmin):
    list_display = ['risk', 'user', 'field', 'timestamp']
    list_filter = ['field', 'timestamp']
    search_fields = ['risk__title']