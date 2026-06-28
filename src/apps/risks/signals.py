from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Risk, RiskHistory

@receiver(pre_save, sender=Risk)
def track_risk_changes(sender, instance, **kwargs):
    """Lưu lịch sử thay đổi trước khi lưu risk"""
    if instance.pk:
        old = Risk.objects.get(pk=instance.pk)
        # So sánh từng field và lưu vào RiskHistory
        fields_to_track = ['title', 'description', 'probability', 'impact', 'status', 'mitigation_plan']
        for field in fields_to_track:
            old_val = getattr(old, field)
            new_val = getattr(instance, field)
            if old_val != new_val:
                RiskHistory.objects.create(
                    risk=instance,
                    user=getattr(instance, '_track_user', None),  # cần set user trước khi save
                    field=field,
                    old_value=str(old_val),
                    new_value=str(new_val)
                )