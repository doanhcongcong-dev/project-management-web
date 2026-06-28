from django.db import models
from django.contrib.auth.models import User
from apps.projects.models import Project

class TestProduct(models.Model):
    RESULT_CHOICES = (
        ('pass', 'Pass'),
        ('fail', 'Fail'),
        ('pending', 'Pending'),
        ('blocked', 'Blocked'),
    )

    project = models.ForeignKey(
        Project, 
        on_delete=models.CASCADE, 
        related_name='test_products'
    )
    name = models.CharField(max_length=200, verbose_name='Tên sản phẩm')
    version = models.CharField(max_length=50, verbose_name='Phiên bản')
    environment = models.CharField(max_length=100, verbose_name='Môi trường test')
    result = models.CharField(
        max_length=20, 
        choices=RESULT_CHOICES, 
        default='pending',
        verbose_name='Kết quả'
    )
    tester = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='test_products',
        verbose_name='Người test'
    )
    test_date = models.DateField(verbose_name='Ngày test')
    notes = models.TextField(blank=True, verbose_name='Ghi chú')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Sản phẩm thử nghiệm'
        verbose_name_plural = 'Sản phẩm thử nghiệm'
        ordering = ['-test_date']

    def __str__(self):
        return f"{self.name} v{self.version} - {self.get_result_display()}"