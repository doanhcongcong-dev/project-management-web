"""
Script đồng bộ dữ liệu từ Wazuh API
Chạy: python scripts/sync_wazuh_alerts.py
"""

import os
import sys
import requests
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR / 'src'))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from django.conf import settings
from apps.wazuh_integration.models import WazuhAlert

def sync_wazuh_alerts():
    """Đồng bộ cảnh báo từ Wazuh"""
    wazuh_url = settings.WAZUH_API_URL
    wazuh_user = settings.WAZUH_API_USER
    wazuh_password = settings.WAZUH_API_PASSWORD

    if not wazuh_url:
        print("⚠️ Wazuh URL chưa được cấu hình")
        return

    try:
        # Login để lấy token
        auth_response = requests.post(
            f'{wazuh_url}/security/user/authenticate',
            auth=(wazuh_user, wazuh_password),
            verify=False
        )
        if auth_response.status_code != 200:
            print("❌ Lỗi xác thực Wazuh")
            return

        token = auth_response.json().get('data', {}).get('token')

        # Lấy alerts
        headers = {'Authorization': f'Bearer {token}'}
        alerts_response = requests.get(
            f'{wazuh_url}/alerts',
            params={'limit': 50},
            headers=headers,
            verify=False
        )

        if alerts_response.status_code != 200:
            print("❌ Không lấy được alerts")
            return

        alerts = alerts_response.json().get('data', {}).get('items', [])

        for alert in alerts:
            alert_id = alert.get('id')
            if not WazuhAlert.objects.filter(alert_id=alert_id).exists():
                WazuhAlert.objects.create(
                    alert_id=alert_id,
                    rule_id=alert.get('rule', {}).get('id'),
                    rule_description=alert.get('rule', {}).get('description', ''),
                    level=alert.get('rule', {}).get('level', 0),
                    timestamp=datetime.fromtimestamp(alert.get('timestamp', 0)),
                    source_ip=alert.get('data', {}).get('srcip'),
                    agent_name=alert.get('agent', {}).get('name', ''),
                    raw_data=alert,
                )
        print(f"✅ Đồng bộ {len(alerts)} alert từ Wazuh")

    except Exception as e:
        print(f"❌ Lỗi đồng bộ Wazuh: {e}")

if __name__ == '__main__':
    sync_wazuh_alerts()