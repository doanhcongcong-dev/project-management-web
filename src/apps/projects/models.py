from django.db import models
from django.contrib.auth.models import User

class Project(models.Model):
    STATUS_CHOICES = (
        ('planning', 'Lên kế hoạch'),
        ('active', 'Đang tiến hành'),
        ('on_hold', 'Tạm dừng'),
        ('completed', 'Hoàn thành'),
        ('cancelled', 'Hủy bỏ'),
    )

    name = models.CharField(max_length=200, verbose_name='Tên dự án')
    description = models.TextField(blank=True, verbose_name='Mô tả')
    start_date = models.DateField(verbose_name='Ngày bắt đầu')
    end_date = models.DateField(null=True, blank=True, verbose_name='Ngày kết thúc')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planning', verbose_name='Trạng thái')
    manager = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_projects',
        verbose_name='Quản lý dự án'
    )
    members = models.ManyToManyField(
        User,
        related_name='projects',
        blank=True,
        verbose_name='Thành viên'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Dự án'
        verbose_name_plural = 'Dự án'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def get_progress(self):
        """Tính tiến độ dự án dựa trên tasks"""
        tasks = self.tasks.all()
        if not tasks.exists():
            return 0
        completed = tasks.filter(status='done').count()
        return int((completed / tasks.count()) * 100)   