from django.db import models
from django.contrib.auth.models import User
from apps.projects.models import Project
from apps.tasks.models import Task

class Milestone(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Chưa hoàn thành'),
        ('in_progress', 'Đang thực hiện'),
        ('completed', 'Hoàn thành'),
        ('delayed', 'Trì hoãn'),
    )

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='milestones',
        verbose_name='Dự án'
    )
    name = models.CharField(max_length=200, verbose_name='Tên cột mốc')
    description = models.TextField(blank=True, verbose_name='Mô tả')
    due_date = models.DateField(verbose_name='Ngày đích')
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Trạng thái'
    )
    tasks = models.ManyToManyField(
        Task,
        blank=True,
        related_name='milestones',
        verbose_name='Công việc liên quan'
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_milestones',
        verbose_name='Người tạo'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='Thời gian hoàn thành')

    class Meta:
        verbose_name = 'Cột mốc'
        verbose_name_plural = 'Cột mốc'
        ordering = ['due_date']

    def __str__(self):
        return f"{self.project.name} - {self.name}"

    def get_progress(self):
        """Tính tiến độ dựa trên các task liên quan"""
        tasks = self.tasks.all()
        if not tasks:
            return 0
        done_tasks = tasks.filter(status='done').count()
        return round((done_tasks / tasks.count()) * 100, 1)

    def is_overdue(self):
        from django.utils import timezone
        return self.due_date < timezone.now().date() and self.status != 'completed'

    def update_status(self):
        """Tự động cập nhật trạng thái dựa trên tiến độ"""
        progress = self.get_progress()
        if progress == 100:
            self.status = 'completed'
            if not self.completed_at:
                from django.utils import timezone
                self.completed_at = timezone.now()
        elif progress > 0:
            self.status = 'in_progress'
        else:
            self.status = 'pending'
        self.save()