import requests
import logging
from django.conf import settings
from datetime import datetime

logger = logging.getLogger(__name__)

def get_wazuh_alerts(limit=100):
    """
    Lấy danh sách alerts từ Wazuh API.
    Trả về list các alert hoặc None nếu lỗi.
    """
    url = f"{settings.WAZUH_API_URL}/alerts"
    headers = {
        'Authorization': f'Bearer {settings.WAZUH_API_TOKEN}',  # nếu dùng token
        'Content-Type': 'application/json',
    }
    params = {
        'limit': limit,
        'sort': '-timestamp',
    }

    try:
        response = requests.get(
            url, 
            headers=headers, 
            params=params, 
            auth=(settings.WAZUH_API_USER, settings.WAZUH_API_PASSWORD) if not settings.WAZUH_API_TOKEN else None,
            verify=False  # chỉ cho dev; production nên dùng cert
        )
        response.raise_for_status()
        data = response.json()
        return data.get('data', {}).get('items', [])
    except requests.RequestException as e:
        logger.error(f"Lỗi khi gọi Wazuh API: {e}")
        return None

def parse_alert(raw_alert):
    """
    Chuyển đổi dữ liệu từ API thành dict để tạo model.
    """
    return {
        'alert_id': raw_alert.get('id'),
        'rule_id': raw_alert.get('rule', {}).get('id'),
        'rule_description': raw_alert.get('rule', {}).get('description', ''),
        'level': raw_alert.get('rule', {}).get('level', 0),
        'timestamp': datetime.fromisoformat(raw_alert.get('timestamp', '').replace('Z', '+00:00')),
        'source_ip': raw_alert.get('data', {}).get('srcip', ''),
        'agent_name': raw_alert.get('agent', {}).get('name', ''),
        'agent_id': raw_alert.get('agent', {}).get('id', ''),
        'raw_data': raw_alert,
    }