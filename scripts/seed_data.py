"""
Script tạo dữ liệu mẫu cho dự án
Chạy: python scripts/seed_data.py
"""

import os
import sys
import random
from pathlib import Path
from datetime import datetime, timedelta
from django.contrib.auth.models import User

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR / 'src'))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from apps.projects.models import Project
from apps.tasks.models import Task
from apps.risks.models import Risk, RiskCategory
from apps.users.models import UserProfile
from apps.notifications.models import Notification

def create_users():
    """Tạo user mẫu"""
    users = []
    for i in range(1, 6):
        username = f'user{i}'
        email = f'user{i}@example.com'
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': email,
                'first_name': f'Người dùng {i}',
                'is_active': True
            }
        )
        if created:
            user.set_password('password123')
            user.save()
            UserProfile.objects.create(user=user)
            print(f"✅ Tạo user: {username}")
        users.append(user)
    return users

def create_projects(users):
    """Tạo dự án mẫu"""
    projects = []
    project_names = [
        'Phát triển hệ thống ERP',
        'Website bán hàng',
        'Ứng dụng di động',
        'Hệ thống quản lý nhân sự',
        'Dự án AI Chatbot'
    ]
    statuses = ['planning', 'active', 'active', 'completed', 'active']

    for i, name in enumerate(project_names):
        project, created = Project.objects.get_or_create(
            name=name,
            defaults={
                'description': f'Dự án {name}',
                'start_date': datetime.now().date() - timedelta(days=random.randint(10, 90)),
                'end_date': datetime.now().date() + timedelta(days=random.randint(30, 120)),
                'status': statuses[i % len(statuses)],
                'manager': random.choice(users)
            }
        )
        if created:
            project.members.set(random.sample(users, k=random.randint(2, 4)))
            print(f"✅ Tạo dự án: {name}")
        projects.append(project)
    return projects

def create_tasks(projects, users):
    """Tạo công việc mẫu"""
    task_titles = [
        'Phân tích yêu cầu',
        'Thiết kế database',
        'Phát triển backend',
        'Phát triển frontend',
        'Test sản phẩm',
        'Triển khai hệ thống',
        'Viết tài liệu',
        'Đào tạo người dùng'
    ]
    priorities = ['low', 'medium', 'high', 'critical']
    statuses = ['new', 'in_progress', 'review', 'done', 'overdue']

    for project in projects:
        for title in random.sample(task_titles, k=random.randint(3, 6)):
            Task.objects.create(
                title=title,
                description=f'Công việc {title} cho dự án {project.name}',
                project=project,
                priority=random.choice(priorities),
                status=random.choice(statuses),
                due_date=datetime.now().date() + timedelta(days=random.randint(5, 30)),
                created_by=random.choice(users),
                progress=random.randint(0, 100)
            )
    print(f"✅ Tạo công việc cho {len(projects)} dự án")

def create_risk_categories():
    """Tạo danh mục rủi ro"""
    categories = [
        'Kỹ thuật', 'Tài chính', 'Nhân sự',
        'Pháp lý', 'Bảo mật', 'Hậu cần'
    ]
    for name in categories:
        RiskCategory.objects.get_or_create(name=name)
    print("✅ Tạo danh mục rủi ro")

def create_risks(projects, users):
    """Tạo rủi ro mẫu"""
    categories = RiskCategory.objects.all()
    for project in projects:
        for _ in range(random.randint(2, 5)):
            Risk.objects.create(
                project=project,
                title=f'Rủi ro {random.choice(["kỹ thuật", "tài chính", "nhân sự"])}',
                description='Mô tả rủi ro chi tiết',
                category=random.choice(categories),
                probability=random.randint(1, 5),
                impact=random.randint(1, 5),
                status=random.choice(['open', 'monitoring', 'mitigated']),
                assigned_to=random.choice(users) if random.choice([True, False]) else None,
                created_by=random.choice(users)
            )
    print(f"✅ Tạo rủi ro cho {len(projects)} dự án")

def main():
    print("🚀 Bắt đầu seed dữ liệu mẫu...")

    # Tạo user
    users = create_users()

    # Tạo danh mục rủi ro
    create_risk_categories()

    # Tạo dự án
    projects = create_projects(users)

    # Tạo công việc
    create_tasks(projects, users)

    # Tạo rủi ro
    create_risks(projects, users)

    print("✅ Seed dữ liệu hoàn tất!")

if __name__ == '__main__':
    main()