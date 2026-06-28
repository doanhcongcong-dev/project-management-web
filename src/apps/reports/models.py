from django.db import models
from django.contrib.auth.models import User
from datetime import datetime

class ReportLog(models.Model):
    """Lưu lịch sử xuất báo cáo (tùy chọn)"""
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    report_type = models.CharField(max_length=50)
    exported_at = models.DateTimeField(auto_now_add=True)
    filters = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"{self.user} - {self.report_type} - {self.exported_at}"