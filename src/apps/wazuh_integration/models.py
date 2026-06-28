from django.db import models
from django.contrib.auth.models import User

class WazuhAlert(models.Model):
    LEVEL_CHOICES = (
        (1, '1 - Low'),
        (2, '2 - Low'),
        (3, '3 - Low'),
        (4, '4 - Medium'),
        (5, '5 - Medium'),
        (6, '6 - Medium'),
        (7, '7 - High'),
        (8, '8 - High'),
        (9, '9 - High'),
        (10, '10 - Critical'),
        (11, '11 - Critical'),
        (12, '12 - Critical'),
        (13, '13 - Critical'),
        (14, '14 - Critical'),
        (15, '15 - Critical'),
    )

    alert_id = models.CharField(max_length=50, unique=True, verbose_name='Alert ID')
    rule_id = models.IntegerField(verbose_name='Rule ID')
    rule_description = models.TextField(verbose_name='Mô tả rule')
    level = models.IntegerField(choices=LEVEL_CHOICES, verbose_name='Mức độ')
    timestamp = models.DateTimeField(verbose_name='Thời gian')
    source_ip = models.GenericIPAddressField(null=True, blank=True, verbose_name='IP nguồn')
    agent_name = models.CharField(max_length=100, blank=True, verbose_name='Tên Agent')
    agent_id = models.CharField(max_length=50, blank=True, verbose_name='Agent ID')
    raw_data = models.JSONField(verbose_name='Dữ liệu thô')
    is_acknowledged = models.BooleanField(default=False, verbose_name='Đã xác nhận')
    acknowledged_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='acknowledged_alerts',
        verbose_name='Xác nhận bởi'
    )
    acknowledged_at = models.DateTimeField(null=True, blank=True, verbose_name='Thời gian xác nhận')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Cảnh báo Wazuh'
        verbose_name_plural = 'Cảnh báo Wazuh'
        ordering = ['-timestamp']

    def __str__(self):
        return f"[{self.level}] {self.rule_description[:30]}"