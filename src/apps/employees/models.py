from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class EmployeeProfile(models.Model):
    """Mở rộng thông tin nhân viên từ User"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee_profile')
    employee_id = models.CharField(max_length=20, unique=True, verbose_name='Mã nhân viên')
    department = models.CharField(max_length=100, verbose_name='Phòng ban')
    position = models.CharField(max_length=100, verbose_name='Chức vụ')
    phone = models.CharField(max_length=15, blank=True, verbose_name='Số điện thoại')
    address = models.TextField(blank=True, verbose_name='Địa chỉ')
    hire_date = models.DateField(verbose_name='Ngày vào làm')
    birth_date = models.DateField(null=True, blank=True, verbose_name='Ngày sinh')
    skills = models.TextField(blank=True, verbose_name='Kỹ năng')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name='Ảnh đại diện')
    is_active = models.BooleanField(default=True, verbose_name='Đang làm việc')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Nhân viên'
        verbose_name_plural = 'Nhân viên'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.employee_id})"

    def get_full_name(self):
        return self.user.get_full_name() or self.user.username

# Tự động tạo EmployeeProfile khi User được tạo
@receiver(post_save, sender=User)
def create_employee_profile(sender, instance, created, **kwargs):
    if created:
        # Tạo employee_id mặc định (có thể custom sau)
        import random
        employee_id = f"EMP{str(random.randint(1000, 9999))}"
        EmployeeProfile.objects.create(
            user=instance,
            employee_id=employee_id,
            department='Chưa phân công',
            position='Nhân viên',
            hire_date=instance.date_joined.date()
        )

@receiver(post_save, sender=User)
def save_employee_profile(sender, instance, **kwargs):
    if not hasattr(instance, 'employee_profile'):
        # Nếu chưa có, tạo mới
        import random
        employee_id = f"EMP{str(random.randint(1000, 9999))}"
        EmployeeProfile.objects.create(
            user=instance,
            employee_id=employee_id,
            department='Chưa phân công',
            position='Nhân viên',
            hire_date=instance.date_joined.date()
        )
    else:
        instance.employee_profile.save()