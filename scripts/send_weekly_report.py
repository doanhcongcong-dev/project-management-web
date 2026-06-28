"""
Script gửi báo cáo tuần qua email
Chạy: python scripts/send_weekly_report.py
"""

import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib.auth.models import User

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR / 'src'))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from apps.projects.models import Project
from apps.tasks.models import Task
from apps.risks.models import Risk

def send_weekly_report():
    """Gửi báo cáo tuần cho admin"""
    week_ago = datetime.now() - timedelta(days=7)

    # Thống kê
    new_projects = Project.objects.filter(created_at__gte=week_ago).count()
    new_tasks = Task.objects.filter(created_at__gte=week_ago).count()
    completed_tasks = Task.objects.filter(status='done', updated_at__gte=week_ago).count()
    new_risks = Risk.objects.filter(created_at__gte=week_ago).count()

    # Lấy danh sách admin
    admins = User.objects.filter(is_staff=True)

    for admin in admins:
        send_mail(
            subject=f'[Báo cáo tuần] {datetime.now().strftime("%d/%m/%Y")}',
            message=f'''
            Báo cáo tuần qua:

            - Dự án mới: {new_projects}
            - Công việc mới: {new_tasks}
            - Công việc hoàn thành: {completed_tasks}
            - Rủi ro mới: {new_risks}

            Xem chi tiết tại: http://localhost:8000/reports/
            ''',
            from_email='noreply@example.com',
            recipient_list=[admin.email],
            fail_silently=False,
        )
        print(f"✅ Đã gửi báo cáo cho {admin.email}")

if __name__ == '__main__':
    send_weekly_report()