from django.db import models
from django.contrib.auth.models import User
from apps.projects.models import Project

class Task(models.Model):
    PRIORITY_CHOICES = (
        ('low', 'Thấp'),
        ('medium', 'Trung bình'),
        ('high', 'Cao'),
        ('critical', 'Khẩn cấp'),
    )

    STATUS_CHOICES = (
        ('new', 'Mới'),
        ('in_progress', 'Đang thực hiện'),
        ('review', 'Chờ duyệt'),
        ('done', 'Hoàn thành'),
        ('overdue', 'Quá hạn'),
    )

    title = models.CharField(max_length=200, verbose_name='Tiêu đề')
    description = models.TextField(blank=True, verbose_name='Mô tả')
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='tasks',
        verbose_name='Dự án'
    )
    assigned_to = models.ManyToManyField(
        User,
        related_name='tasks',
        verbose_name='Người được giao'
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_tasks',
        verbose_name='Người tạo'
    )
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='medium',
        verbose_name='Ưu tiên'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='new',
        verbose_name='Trạng thái'
    )
    due_date = models.DateField(verbose_name='Hạn hoàn thành')
    progress = models.IntegerField(default=0, verbose_name='Tiến độ (%)')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Công việc'
        verbose_name_plural = 'Công việc'
        ordering = ['-due_date', '-priority']

    def __str__(self):
        return self.title

    def is_overdue(self):
        """Kiểm tra nếu task quá hạn nhưng chưa hoàn thành"""
        from django.utils import timezone
        if self.status != 'done' and self.due_date < timezone.now().date():
            return True
        return False