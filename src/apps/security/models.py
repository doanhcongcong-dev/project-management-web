from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class SecurityLog(models.Model):
    """Ghi log mọi hành động quan trọng"""
    ACTION_CHOICES = (
        ('login', 'Đăng nhập'),
        ('logout', 'Đăng xuất'),
        ('create', 'Tạo mới'),
        ('update', 'Cập nhật'),
        ('delete', 'Xóa'),
        ('view', 'Xem'),
        ('export', 'Xuất dữ liệu'),
        ('2fa_enable', 'Bật 2FA'),
        ('2fa_disable', 'Tắt 2FA'),
        ('other', 'Khác'),
    )

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=50, choices=ACTION_CHOICES, default='other')
    description = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_type = models.CharField(max_length=100, blank=True)

    class Meta:
        verbose_name = 'Log bảo mật'
        verbose_name_plural = 'Log bảo mật'
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user} - {self.get_action_display()} - {self.timestamp}"


class User2FA(models.Model):
    """Lưu thông tin 2FA cho từng user"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='twofa')
    secret = models.CharField(max_length=32, blank=True)  # TOTP secret
    is_enabled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - 2FA {'enabled' if self.is_enabled else 'disabled'}"