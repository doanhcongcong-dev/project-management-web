from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from .models import Notification
from apps.tasks.models import Task
from apps.projects.models import Project
from apps.risks.models import Risk
from django.contrib.auth.models import User

@receiver(m2m_changed, sender=Task.assigned_to.through)
def notify_task_assigned(sender, instance, action, reverse, model, pk_set, **kwargs):
    """Gửi thông báo khi task được giao cho user"""
    if action == 'post_add':
        for user_pk in pk_set:
            user = model.objects.get(pk=user_pk)
            Notification.objects.create(
                recipient=user,
                sender=instance.created_by,
                title=f'Công việc mới: {instance.title}',
                message=f'Bạn được giao công việc "{instance.title}" trong dự án "{instance.project.name}". Hạn: {instance.due_date.strftime("%d/%m/%Y")}',
                link=f'/tasks/{instance.pk}/'
            )

@receiver(post_save, sender=Task)
def notify_task_status_change(sender, instance, created, **kwargs):
    """Thông báo khi task thay đổi trạng thái (ví dụ: hoàn thành)"""
    if not created and instance.status == 'done':
        for user in instance.assigned_to.all():
            if user != instance.created_by:  # nếu người tạo không phải người nhận
                Notification.objects.create(
                    recipient=user,
                    sender=instance.created_by,
                    title=f'Công việc hoàn thành: {instance.title}',
                    message=f'Công việc "{instance.title}" đã được hoàn thành bởi {instance.created_by.username}.',
                    link=f'/tasks/{instance.pk}/'
                )

@receiver(post_save, sender=Project)
def notify_project_created(sender, instance, created, **kwargs):
    """Thông báo khi tạo dự án mới"""
    if created:
        # Gửi cho tất cả thành viên
        for member in instance.members.all():
            Notification.objects.create(
                recipient=member,
                sender=instance.manager,
                title=f'Dự án mới: {instance.name}',
                message=f'Dự án "{instance.name}" vừa được tạo bởi {instance.manager.username}.',
                link=f'/projects/{instance.pk}/'
            )

@receiver(post_save, sender=Risk)
def notify_risk_created(sender, instance, created, **kwargs):
    """Thông báo khi có rủi ro mới"""
    if created and instance.assigned_to:
        Notification.objects.create(
            recipient=instance.assigned_to,
            sender=instance.created_by,
            title=f'Rủi ro mới: {instance.title}',
            message=f'Rủi ro "{instance.title}" được tạo trong dự án "{instance.project.name}". Mức độ: {instance.get_risk_level()[0]}',
            link=f'/risks/{instance.pk}/'
        )