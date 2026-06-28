from django.db.models.signals import post_save, post_delete
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import ActivityLog
from .utils import get_client_ip, get_user_agent

# Ghi log đăng nhập/đăng xuất
@receiver(user_logged_in)
def log_login(sender, request, user, **kwargs):
    ActivityLog.objects.create(
        user=user,
        action='login',
        description=f'Đăng nhập từ IP {get_client_ip(request)}',
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
        url=request.build_absolute_uri(),
        method='POST'
    )

@receiver(user_logged_out)
def log_logout(sender, request, user, **kwargs):
    if user:
        ActivityLog.objects.create(
            user=user,
            action='logout',
            description='Đăng xuất',
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
            url=request.build_absolute_uri(),
            method='POST'
        )

# Ghi log khi tạo/sửa/xóa user (ví dụ)
@receiver(post_save, sender=User)
def log_user_change(sender, instance, created, **kwargs):
    if created:
        ActivityLog.objects.create(
            user=instance,
            action='create',
            description=f'Tạo tài khoản mới: {instance.username}',
            object_id=instance.id,
            content_type='user'
        )
    else:
        # Có thể ghi log sửa, nhưng sẽ gọi nhiều lần, cần cẩn thận
        pass

@receiver(post_delete, sender=User)
def log_user_delete(sender, instance, **kwargs):
    ActivityLog.objects.create(
        user=instance,
        action='delete',
        description=f'Xóa tài khoản: {instance.username}',
        object_id=instance.id,
        content_type='user'
    )