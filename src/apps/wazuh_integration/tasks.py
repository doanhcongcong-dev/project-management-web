from celery import shared_task
from .models import WazuhAlert
from .utils import get_wazuh_alerts, parse_alert
import logging

logger = logging.getLogger(__name__)

@shared_task
def sync_wazuh_alerts():
    """
    Đồng bộ alerts mới từ Wazuh vào database.
    """
    logger.info("Bắt đầu đồng bộ Wazuh alerts...")
    alerts = get_wazuh_alerts(limit=100)
    if alerts is None:
        logger.error("Không thể lấy alerts từ Wazuh API.")
        return
    
    created_count = 0
    for raw_alert in alerts:
        alert_id = raw_alert.get('id')
        if not alert_id:
            continue
        # Kiểm tra xem đã tồn tại chưa
        if WazuhAlert.objects.filter(alert_id=alert_id).exists():
            continue
        
        # Tạo mới
        parsed = parse_alert(raw_alert)
        WazuhAlert.objects.create(**parsed)
        created_count += 1
    
    logger.info(f"Đã đồng bộ {created_count} alerts mới.")
    return created_count