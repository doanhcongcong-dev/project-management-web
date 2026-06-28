from django.db import models
from django.contrib.auth.models import User
from apps.projects.models import Project

class ChatRoom(models.Model):
    """Phòng chat cho mỗi dự án"""
    project = models.OneToOneField(
        Project,
        on_delete=models.CASCADE,
        related_name='chat_room',
        verbose_name='Dự án'
    )
    name = models.CharField(max_length=100, verbose_name='Tên phòng')
    members = models.ManyToManyField(
        User,
        related_name='chat_rooms',
        verbose_name='Thành viên'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Phòng chat'
        verbose_name_plural = 'Phòng chat'
        ordering = ['-updated_at']

    def __str__(self):
        return f"Chat - {self.project.name}"

    def get_last_message(self):
        """Lấy tin nhắn cuối cùng trong phòng"""
        return self.messages.order_by('-timestamp').first()


class Message(models.Model):
    """Tin nhắn trong phòng chat"""
    room = models.ForeignKey(
        ChatRoom,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name='Phòng chat'
    )
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_messages',
        verbose_name='Người gửi'
    )
    content = models.TextField(verbose_name='Nội dung')
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False, verbose_name='Đã đọc')

    class Meta:
        verbose_name = 'Tin nhắn'
        verbose_name_plural = 'Tin nhắn'
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.sender.username}: {self.content[:30]}"