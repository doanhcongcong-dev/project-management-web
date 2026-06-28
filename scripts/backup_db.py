"""
Script backup database PostgreSQL
Chạy: python scripts/backup_db.py
"""

import os
import sys
import datetime
import subprocess
from pathlib import Path

# Thêm đường dẫn dự án vào sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR / 'src'))

# Load settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from django.conf import settings

def backup_database():
    """Backup PostgreSQL database"""
    db_name = settings.DATABASES['default']['NAME']
    db_user = settings.DATABASES['default']['USER']
    db_password = settings.DATABASES['default']['PASSWORD']
    db_host = settings.DATABASES['default']['HOST']
    db_port = settings.DATABASES['default']['PORT']

    # Tạo thư mục backup nếu chưa có
    backup_dir = BASE_DIR / 'backups'
    backup_dir.mkdir(exist_ok=True)

    # Tên file backup
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = backup_dir / f'backup_{db_name}_{timestamp}.sql'

    # Lệnh pg_dump
    cmd = [
        'pg_dump',
        f'--dbname=postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}',
        '--format=plain',
        '--no-owner',
        '--no-acl',
        '--file', str(backup_file)
    ]

    try:
        subprocess.run(cmd, check=True)
        print(f"✅ Backup thành công: {backup_file}")
        # Nén file
        subprocess.run(['gzip', str(backup_file)], check=True)
        print(f"✅ Đã nén: {backup_file}.gz")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Backup thất bại: {e}")
        return False

if __name__ == '__main__':
    backup_database()