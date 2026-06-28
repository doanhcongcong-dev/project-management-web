from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from .models import Milestone
from apps.tasks.models import Task

@receiver(post_save, sender=Task)
@receiver(m2m_changed, sender=Milestone.tasks.through)
def update_milestone_status(sender, instance, **kwargs):
    """Cập nhật trạng thái của milestone khi task thay đổi"""
    # Nếu là task, tìm tất cả milestone liên quan
    if isinstance(instance, Task):
        milestones = instance.milestones.all()
        for milestone in milestones:
            milestone.update_status()
    # Nếu là milestone, chỉ cập nhật chính nó
    elif isinstance(instance, Milestone):
        instance.update_status()