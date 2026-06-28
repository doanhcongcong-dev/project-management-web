from django.contrib import admin
from .models import Document

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['name', 'project', 'document_type', 'version', 'uploaded_by', 'uploaded_at']
    list_filter = ['document_type', 'project', 'uploaded_at']
    search_fields = ['name', 'description']
    date_hierarchy = 'uploaded_at'
    raw_id_fields = ['project', 'uploaded_by']