from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q, Sum
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from apps.projects.models import Project
from apps.tasks.models import Task
from apps.risks.models import Risk
from apps.employees.models import EmployeeProfile
from apps.test_products.models import TestProduct
from apps.users.models import UserProfile
from datetime import datetime, timedelta
from django.utils import timezone
from django.contrib.auth.models import User 
import json

@login_required
def dashboard(request):
    """Trang tổng quan với các thống kê"""
    # Thống kê chung
    total_projects = Project.objects.count()
    active_projects = Project.objects.filter(status__in=['active', 'planning']).count()
    completed_projects = Project.objects.filter(status='completed').count()

    total_tasks = Task.objects.count()
    overdue_tasks = Task.objects.filter(status='overdue').count()
    completed_tasks = Task.objects.filter(status='done').count()

    total_risks = Risk.objects.count()
    open_risks = Risk.objects.filter(status__in=['open', 'monitoring']).count()
    high_risks = Risk.objects.filter(probability__gte=4, impact__gte=4).count()

    total_employees = EmployeeProfile.objects.count() or UserProfile.objects.count()
    total_test_products = TestProduct.objects.count()
    pass_tests = TestProduct.objects.filter(result='pass').count()
    fail_tests = TestProduct.objects.filter(result='fail').count()

    # Thống kê task theo người dùng (cho biểu đồ)
    task_by_assignee = Task.objects.values('assigned_to__username').annotate(count=Count('id')).order_by('-count')[:10]

    # Thống kê task theo dự án
    task_by_project = Project.objects.annotate(task_count=Count('tasks')).values('name', 'task_count').order_by('-task_count')[:10]

    # Biểu đồ tiến độ dự án (dùng cho Chart.js)
    project_progress = Project.objects.filter(status__in=['active', 'planning']).values('name', 'id')[:10]

    # Lấy 10 dự án gần đây
    recent_projects = Project.objects.order_by('-created_at')[:5]

    # Lấy 10 task quá hạn
    recent_overdue_tasks = Task.objects.filter(status='overdue').order_by('due_date')[:5]

    context = {
        'total_projects': total_projects,
        'active_projects': active_projects,
        'completed_projects': completed_projects,
        'total_tasks': total_tasks,
        'overdue_tasks': overdue_tasks,
        'completed_tasks': completed_tasks,
        'total_risks': total_risks,
        'open_risks': open_risks,
        'high_risks': high_risks,
        'total_employees': total_employees,
        'total_test_products': total_test_products,
        'pass_tests': pass_tests,
        'fail_tests': fail_tests,
        'task_by_assignee': task_by_assignee,
        'task_by_project': task_by_project,
        'project_progress': project_progress,
        'recent_projects': recent_projects,
        'recent_overdue_tasks': recent_overdue_tasks,
    }
    return render(request, 'reports/dashboard.html', context)

@login_required
def project_report(request):
    """Báo cáo chi tiết theo dự án"""
    projects = Project.objects.all().annotate(
        task_count=Count('tasks'),
        completed_task_count=Count('tasks', filter=Q(tasks__status='done')),
        overdue_task_count=Count('tasks', filter=Q(tasks__status='overdue')),
        risk_count=Count('risks'),
        open_risk_count=Count('risks', filter=Q(risks__status__in=['open', 'monitoring'])),
    ).order_by('name')

    # Lọc theo dự án
    project_id = request.GET.get('project_id')
    if project_id:
        projects = projects.filter(id=project_id)

    context = {
        'projects': projects,
        'project_id': project_id,
    }
    return render(request, 'reports/project_report.html', context)

@login_required
def task_report(request):
    """Báo cáo chi tiết về task"""
    tasks = Task.objects.all().select_related('project', 'created_by')

    # Lọc theo dự án
    project_id = request.GET.get('project')
    if project_id:
        tasks = tasks.filter(project_id=project_id)

    # Lọc theo trạng thái
    status = request.GET.get('status')
    if status:
        tasks = tasks.filter(status=status)

    # Tìm kiếm
    search = request.GET.get('search')
    if search:
        tasks = tasks.filter(title__icontains=search)

    tasks = tasks.order_by('-created_at')

    # Thống kê
    total = tasks.count()
    by_status = tasks.values('status').annotate(count=Count('id'))
    by_priority = tasks.values('priority').annotate(count=Count('id'))

    context = {
        'tasks': tasks,
        'total': total,
        'by_status': by_status,
        'by_priority': by_priority,
        'project_id': project_id,
        'status': status,
        'search': search,
    }
    return render(request, 'reports/task_report.html', context)

@login_required
def employee_report(request):
    """Báo cáo hiệu suất nhân viên"""
    from django.contrib.auth.models import User
    users = User.objects.filter(is_active=True)

    # Lọc theo phòng ban nếu có (tùy chỉnh)
    department = request.GET.get('department')
    if department:
        users = users.filter(profile__department=department)

    # Tổng hợp số task được giao, hoàn thành, quá hạn cho mỗi user
    employee_data = []
    for user in users:
        tasks = Task.objects.filter(assigned_to=user)
        total_assigned = tasks.count()
        completed = tasks.filter(status='done').count()
        overdue = tasks.filter(status='overdue').count()
        progress = 0
        if total_assigned > 0:
            progress = int((completed / total_assigned) * 100)
        employee_data.append({
            'user': user,
            'total_assigned': total_assigned,
            'completed': completed,
            'overdue': overdue,
            'progress': progress,
        })

    # Sắp xếp theo số task hoàn thành
    employee_data.sort(key=lambda x: x['completed'], reverse=True)

    context = {
        'employee_data': employee_data,
        'department': department,
    }
    return render(request, 'reports/employee_report.html', context)

# API view (cho biểu đồ dashboard - nếu dùng AJAX)
@login_required
def chart_data(request):
    """Trả về dữ liệu JSON cho biểu đồ"""
    data = {
        'labels': ['Projects', 'Tasks', 'Risks', 'Tests'],
        'values': [
            Project.objects.count(),
            Task.objects.count(),
            Risk.objects.count(),
            TestProduct.objects.count()
        ]
    }
    return JsonResponse(data)