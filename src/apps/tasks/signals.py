from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from .models import Task
from apps.notifications.models import Notification

@receiver(m2m_changed, sender=Task.assigned_to.through)
def notify_assigned_users(sender, instance, action, reverse, model, pk_set, **kwargs):
    """Gửi thông báo khi task được giao cho người dùng"""
    if action == 'post_add':
        for user_pk in pk_set:
            user = model.objects.get(pk=user_pk)
            Notification.objects.create(
                recipient=user,
                message=f'Bạn được giao công việc "{instance.title}" trong dự án "{instance.project.name}"',
                link=f'/tasks/{instance.pk}/'
            )