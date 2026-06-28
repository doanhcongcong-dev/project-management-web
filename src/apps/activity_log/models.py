from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class ActivityLog(models.Model):
    ACTION_CHOICES = (
        ('login', 'Đăng nhập'),
        ('logout', 'Đăng xuất'),
        ('create', 'Tạo mới'),
        ('update', 'Cập nhật'),
        ('delete', 'Xóa'),
        ('view', 'Xem'),
        ('export', 'Xuất dữ liệu'),
        ('upload', 'Tải lên'),
        ('download', 'Tải xuống'),
        ('2fa_enable', 'Bật 2FA'),
        ('2fa_disable', 'Tắt 2FA'),
        ('other', 'Khác'),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='activity_logs',
        verbose_name='Người dùng'
    )
    action = models.CharField(
        max_length=50,
        choices=ACTION_CHOICES,
        default='other',
        verbose_name='Hành động'
    )
    description = models.TextField(blank=True, verbose_name='Mô tả')
    ip_address = models.GenericIPAddressField(blank=True, null=True, verbose_name='Địa chỉ IP')
    user_agent = models.TextField(blank=True, verbose_name='User Agent')
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name='Thời gian')
    object_id = models.PositiveIntegerField(null=True, blank=True, verbose_name='ID đối tượng')
    content_type = models.CharField(max_length=100, blank=True, verbose_name='Loại đối tượng')
    url = models.URLField(max_length=500, blank=True, verbose_name='URL')
    method = models.CharField(max_length=10, blank=True, verbose_name='Phương thức HTTP')

    class Meta:
        verbose_name = 'Nhật ký hoạt động'
        verbose_name_plural = 'Nhật ký hoạt động'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['action', 'timestamp']),
        ]

    def __str__(self):
        return f"{self.user.username if self.user else 'Anonymous'} - {self.get_action_display()} - {self.timestamp.strftime('%d/%m/%Y %H:%M')}"