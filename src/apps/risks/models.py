from django.db import models
from django.contrib.auth.models import User
from apps.projects.models import Project

class RiskCategory(models.Model):
    """Danh mục rủi ro (ví dụ: Kỹ thuật, Tài chính, Nhân sự, ...)"""
    name = models.CharField(max_length=100, unique=True, verbose_name='Tên danh mục')
    description = models.TextField(blank=True, verbose_name='Mô tả')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Danh mục rủi ro'
        verbose_name_plural = 'Danh mục rủi ro'
        ordering = ['name']

    def __str__(self):
        return self.name


class Risk(models.Model):
    """Rủi ro trong dự án"""
    PROBABILITY_CHOICES = (
        (1, 'Rất thấp (1)'),
        (2, 'Thấp (2)'),
        (3, 'Trung bình (3)'),
        (4, 'Cao (4)'),
        (5, 'Rất cao (5)'),
    )

    IMPACT_CHOICES = (
        (1, 'Rất thấp (1)'),
        (2, 'Thấp (2)'),
        (3, 'Trung bình (3)'),
        (4, 'Cao (4)'),
        (5, 'Rất cao (5)'),
    )

    STATUS_CHOICES = (
        ('open', 'Mở'),
        ('monitoring', 'Đang giám sát'),
        ('mitigated', 'Đã giảm thiểu'),
        ('closed', 'Đóng'),
        ('accepted', 'Chấp nhận'),
    )

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='risks',
        verbose_name='Dự án'
    )
    category = models.ForeignKey(
        RiskCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='risks',
        verbose_name='Danh mục'
    )
    title = models.CharField(max_length=200, verbose_name='Tiêu đề')
    description = models.TextField(verbose_name='Mô tả chi tiết')
    probability = models.IntegerField(
        choices=PROBABILITY_CHOICES,
        default=3,
        verbose_name='Xác suất'
    )
    impact = models.IntegerField(
        choices=IMPACT_CHOICES,
        default=3,
        verbose_name='Tác động'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='open',
        verbose_name='Trạng thái'
    )
    mitigation_plan = models.TextField(
        blank=True,
        verbose_name='Kế hoạch giảm thiểu'
    )
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_risks',
        verbose_name='Người phụ trách'
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_risks',
        verbose_name='Người tạo'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    closed_at = models.DateTimeField(null=True, blank=True, verbose_name='Ngày đóng')

    class Meta:
        verbose_name = 'Rủi ro'
        verbose_name_plural = 'Rủi ro'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.project.name} - {self.title}"

    def risk_score(self):
        """Tính điểm rủi ro = xác suất * tác động"""
        return self.probability * self.impact

    def get_risk_level(self):
        """Phân cấp độ rủi ro"""
        score = self.risk_score()
        if score >= 20:
            return 'Cao', 'danger'
        elif score >= 10:
            return 'Trung bình', 'warning'
        else:
            return 'Thấp', 'success'


class RiskHistory(models.Model):
    """Lịch sử thay đổi rủi ro (dùng để audit)"""
    risk = models.ForeignKey(Risk, on_delete=models.CASCADE, related_name='history')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    field = models.CharField(max_length=50, verbose_name='Trường thay đổi')
    old_value = models.TextField(blank=True)
    new_value = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Lịch sử rủi ro'
        verbose_name_plural = 'Lịch sử rủi ro'
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.risk} - {self.field} changed at {self.timestamp}"