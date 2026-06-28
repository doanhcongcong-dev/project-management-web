from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.projects.models import Project
from .models import ChatRoom

@receiver(post_save, sender=Project)
def create_chat_room(sender, instance, created, **kwargs):
    """Tự động tạo phòng chat khi dự án được tạo"""
    if created:
        ChatRoom.objects.create(
            project=instance,
            name=f"Chat - {instance.name}"
        )

@receiver(post_save, sender=Project)
def update_chat_room_members(sender, instance, **kwargs):
    """Cập nhật thành viên phòng chat khi dự án thay đổi thành viên"""
    # Có thể dùng m2m_changed signal để cập nhật members
    pass