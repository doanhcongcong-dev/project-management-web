from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import Document

@receiver(pre_save, sender=Document)
def increment_version_on_new_file(sender, instance, **kwargs):
    """Nếu file được thay đổi, tự động tăng version"""
    if instance.pk:
        old = sender.objects.get(pk=instance.pk)
        if old.file != instance.file:
            # Tăng phiên bản (ví dụ 1.0 -> 1.1)
            version_parts = old.version.split('.')
            if len(version_parts) == 2:
                major, minor = version_parts
                minor = str(int(minor) + 1)
                instance.version = f"{major}.{minor}"
            else:
                instance.version = f"{old.version}.1"