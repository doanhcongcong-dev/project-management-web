from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
import json

from apps.projects.models import Project
from apps.tasks.models import Task
from apps.risks.models import Risk
from apps.notifications.models import Notification
from apps.documents.models import Document
from apps.test_products.models import TestProduct

@login_required
def index(request):
    """
    Dashboard tổng quan – nội dung khác nhau tùy theo vai trò user
    """
    user = request.user
    is_staff = user.is_staff
    is_manager = user.groups.filter(name='Quản lý dự án').exists() or user.is_superuser

    # ---- Thống kê chung ----
    # Tổng số dự án, công việc, rủi ro, tài liệu, thông báo
    total_projects = Project.objects.count()
    total_tasks = Task.objects.count()
    total_risks = Risk.objects.count()
    total_documents = Document.objects.count()
    total_notifications = Notification.objects.filter(recipient=user).count()

    # ---- Dành cho nhân viên (và admin có thể xem thêm) ----
    # Công việc được giao cho user
    my_tasks = Task.objects.filter(assigned_to=user)
    my_tasks_count = my_tasks.count()
    my_tasks_done = my_tasks.filter(status='done').count()
    my_tasks_overdue = my_tasks.filter(status='overdue').count()
    my_tasks_in_progress = my_tasks.filter(status='in_progress').count()

    # Dự án user tham gia
    my_projects = Project.objects.filter(members=user)
    my_projects_count = my_projects.count()

    # Thông báo chưa đọc
    unread_notifications = Notification.objects.filter(recipient=user, is_read=False)
    unread_count = unread_notifications.count()
    latest_notifications = unread_notifications.order_by('-created_at')[:5]

    # ---- Thống kê cho quản lý/admin ----
    if is_staff or is_manager:
        # Số dự án theo trạng thái
        project_stats = {
            'planning': Project.objects.filter(status='planning').count(),
            'active': Project.objects.filter(status='active').count(),
            'on_hold': Project.objects.filter(status='on_hold').count(),
            'completed': Project.objects.filter(status='completed').count(),
        }
        # Số công việc theo trạng thái
        task_stats = {
            'new': Task.objects.filter(status='new').count(),
            'in_progress': Task.objects.filter(status='in_progress').count(),
            'review': Task.objects.filter(status='review').count(),
            'done': Task.objects.filter(status='done').count(),
            'overdue': Task.objects.filter(status='overdue').count(),
        }
        # Rủi ro theo mức độ
        risk_stats = {
            'high': Risk.objects.filter(probability__gte=4, impact__gte=4).count(),
            'medium': Risk.objects.filter(probability__gte=3, impact__gte=3).exclude(probability__gte=4, impact__gte=4).count(),
            'low': Risk.objects.exclude(probability__gte=3, impact__gte=3).count(),
        }
        # Danh sách dự án sắp kết thúc
        upcoming_deadline = Project.objects.filter(
            status='active',
            end_date__gte=timezone.now().date()
        ).order_by('end_date')[:5]

        # Danh sách task quá hạn (nổi bật)
        overdue_tasks = Task.objects.filter(status='overdue').select_related('project', 'created_by')[:10]

        context = {
            'is_admin_or_manager': True,
            'total_projects': total_projects,
            'total_tasks': total_tasks,
            'total_risks': total_risks,
            'total_documents': total_documents,
            'total_notifications': total_notifications,
            'my_tasks_count': my_tasks_count,
            'my_tasks_done': my_tasks_done,
            'my_tasks_overdue': my_tasks_overdue,
            'my_tasks_in_progress': my_tasks_in_progress,
            'my_projects_count': my_projects_count,
            'unread_count': unread_count,
            'latest_notifications': latest_notifications,
            'project_stats': json.dumps(project_stats),
            'task_stats': json.dumps(task_stats),
            'risk_stats': json.dumps(risk_stats),
            'upcoming_deadline': upcoming_deadline,
            'overdue_tasks': overdue_tasks,
        }
    else:
        # Nhân viên bình thường
        context = {
            'is_admin_or_manager': False,
            'total_projects': total_projects,
            'total_tasks': total_tasks,
            'total_risks': total_risks,
            'total_documents': total_documents,
            'total_notifications': total_notifications,
            'my_tasks_count': my_tasks_count,
            'my_tasks_done': my_tasks_done,
            'my_tasks_overdue': my_tasks_overdue,
            'my_tasks_in_progress': my_tasks_in_progress,
            'my_projects_count': my_projects_count,
            'unread_count': unread_count,
            'latest_notifications': latest_notifications,
            # Danh sách các task của user sắp đến hạn
            'my_upcoming_tasks': my_tasks.filter(
                status__in=['new', 'in_progress'],
                due_date__lte=timezone.now().date() + timedelta(days=3)
            ).order_by('due_date')[:5],
        }

    return render(request, 'dashboard/index.html', context)