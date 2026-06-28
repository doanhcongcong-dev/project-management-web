"""
Script xóa log cũ để tiết kiệm database
Chạy: python scripts/cleanup_old_logs.py --days=30
"""

import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
import argparse

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR / 'src'))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from apps.activity_log.models import ActivityLog
from apps.security.models import SecurityLog

def cleanup_logs(days=30):
    """Xóa log cũ hơn số ngày chỉ định"""
    cutoff_date = datetime.now() - timedelta(days=days)

    # ActivityLog
    activity_count = ActivityLog.objects.filter(timestamp__lt=cutoff_date).count()
    ActivityLog.objects.filter(timestamp__lt=cutoff_date).delete()
    print(f"✅ Đã xóa {activity_count} ActivityLog cũ hơn {days} ngày")

    # SecurityLog
    security_count = SecurityLog.objects.filter(timestamp__lt=cutoff_date).count()
    SecurityLog.objects.filter(timestamp__lt=cutoff_date).delete()
    print(f"✅ Đã xóa {security_count} SecurityLog cũ hơn {days} ngày")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--days', type=int, default=30, help='Số ngày giữ lại')
    args = parser.parse_args()

    print(f"🚀 Xóa log cũ hơn {args.days} ngày...")
    cleanup_logs(args.days)