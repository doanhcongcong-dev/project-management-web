from django.db.models.signals import post_save, post_delete
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import SecurityLog

# Ghi log đăng nhập/đăng xuất
@receiver(user_logged_in)
def log_login(sender, request, user, **kwargs):
    SecurityLog.objects.create(
        user=user,
        action='login',
        description=f'Đăng nhập từ IP {request.META.get("REMOTE_ADDR")}',
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT', '')
    )

@receiver(user_logged_out)
def log_logout(sender, request, user, **kwargs):
    if user:
        SecurityLog.objects.create(
            user=user,
            action='logout',
            description='Đăng xuất',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )

# Ghi log khi tạo/sửa/xóa user (ví dụ)
@receiver(post_save, sender=User)
def log_user_change(sender, instance, created, **kwargs):
    if created:
        SecurityLog.objects.create(
            user=instance,
            action='create',
            description=f'Tạo tài khoản mới: {instance.username}',
            content_type='user',
            object_id=instance.id
        )
    else:
        # Có thể ghi log sửa, nhưng sẽ bị gọi nhiều lần, nên tùy chỉnh
        pass

@receiver(post_delete, sender=User)
def log_user_delete(sender, instance, **kwargs):
    SecurityLog.objects.create(
        user=instance,
        action='delete',
        description=f'Xóa tài khoản: {instance.username}',
        content_type='user',
        object_id=instance.id
    )