from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from .models import Task
from .forms import TaskForm, TaskProgressForm
from apps.projects.models import Project
from apps.notifications.models import Notification

@login_required
def my_tasks(request):
    """Danh sách công việc của tôi (người dùng hiện tại)"""
    tasks = Task.objects.filter(assigned_to=request.user).select_related('project')
    
    # Lọc theo trạng thái
    status_filter = request.GET.get('status')
    if status_filter:
        tasks = tasks.filter(status=status_filter)
    
    # Tìm kiếm
    search = request.GET.get('search')
    if search:
        tasks = tasks.filter(
            Q(title__icontains=search) | Q(description__icontains=search)
        )
    
    paginator = Paginator(tasks, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search,
        'status_filter': status_filter,
    }
    return render(request, 'tasks/my_tasks.html', context)

@login_required
def list_view(request):
    """Danh sách tất cả công việc (dành cho admin/manager)"""
    if not request.user.is_staff and not request.user.has_perm('tasks.view_task'):
        messages.error(request, 'Bạn không có quyền xem tất cả công việc.')
        return redirect('tasks:my_tasks')
    
    tasks = Task.objects.all().select_related('project', 'created_by')
    
    # Lọc theo dự án
    project_id = request.GET.get('project')
    if project_id:
        tasks = tasks.filter(project_id=project_id)
    
    # Lọc theo trạng thái
    status = request.GET.get('status')
    if status:
        tasks = tasks.filter(status=status)
    
    # Lọc theo người được giao
    assigned = request.GET.get('assigned')
    if assigned:
        tasks = tasks.filter(assigned_to__id=assigned)
    
    # Tìm kiếm
    search = request.GET.get('search')
    if search:
        tasks = tasks.filter(
            Q(title__icontains=search) | Q(description__icontains=search)
        )
    
    paginator = Paginator(tasks, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Lấy danh sách project và user để hiển thị filter
    projects = Project.objects.all()
    users = User.objects.filter(is_active=True)
    
    context = {
        'page_obj': page_obj,
        'projects': projects,
        'users': users,
        'selected_project': project_id,
        'selected_status': status,
        'selected_assigned': assigned,
        'search_query': search,
    }
    return render(request, 'tasks/list.html', context)

@login_required
def detail_view(request, pk):
    task = get_object_or_404(Task, pk=pk)
    # Kiểm tra quyền: người dùng phải là người được giao hoặc admin/manager
    if not (request.user in task.assigned_to.all() or request.user.is_staff or request.user == task.created_by):
        messages.error(request, 'Bạn không có quyền xem công việc này.')
        return redirect('tasks:my_tasks')
    
    return render(request, 'tasks/detail.html', {'task': task})

@login_required
def create_view(request):
    """Tạo công việc mới"""
    if not (request.user.is_staff or request.user.has_perm('tasks.add_task')):
        messages.error(request, 'Bạn không có quyền tạo công việc.')
        return redirect('tasks:my_tasks')
    
    if request.method == 'POST':
        form = TaskForm(request.POST, user=request.user)
        if form.is_valid():
            task = form.save(commit=False)
            task.created_by = request.user
            task.save()
            form.save_m2m()  # Lưu assigned_to (ManyToMany)
            messages.success(request, 'Tạo công việc thành công!')
            return redirect('tasks:detail', pk=task.pk)
    else:
        # Pre-fill project nếu có param
        initial = {}
        project_id = request.GET.get('project')
        if project_id:
            initial['project'] = project_id
        form = TaskForm(user=request.user, initial=initial)
    
    return render(request, 'tasks/create.html', {'form': form})

@login_required
def edit_view(request, pk):
    task = get_object_or_404(Task, pk=pk)
    # Kiểm tra quyền: chỉ người tạo hoặc admin/manager mới được sửa
    if not (request.user == task.created_by or request.user.is_staff or request.user.has_perm('tasks.change_task')):
        messages.error(request, 'Bạn không có quyền chỉnh sửa công việc này.')
        return redirect('tasks:detail', pk=pk)
    
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cập nhật công việc thành công!')
            return redirect('tasks:detail', pk=pk)
    else:
        form = TaskForm(instance=task, user=request.user)
    
    return render(request, 'tasks/edit.html', {'form': form, 'task': task})

@login_required
def delete_view(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if not (request.user == task.created_by or request.user.is_staff or request.user.has_perm('tasks.delete_task')):
        messages.error(request, 'Bạn không có quyền xóa công việc này.')
        return redirect('tasks:detail', pk=pk)
    
    if request.method == 'POST':
        task.delete()
        messages.success(request, 'Công việc đã được xóa.')
        return redirect('tasks:list')
    
    return render(request, 'tasks/confirm_delete.html', {'task': task})

@login_required
def update_progress(request, pk):
    """Cập nhật tiến độ công việc (dành cho người được giao)"""
    task = get_object_or_404(Task, pk=pk)
    if request.user not in task.assigned_to.all() and not request.user.is_staff:
        messages.error(request, 'Bạn không có quyền cập nhật tiến độ công việc này.')
        return redirect('tasks:detail', pk=pk)
    
    if request.method == 'POST':
        form = TaskProgressForm(request.POST, instance=task)
        if form.is_valid():
            task = form.save()
            # Nếu progress = 100, tự động chuyển status thành done
            if task.progress == 100 and task.status != 'done':
                task.status = 'done'
                task.save()
            messages.success(request, 'Cập nhật tiến độ thành công!')
            return redirect('tasks:detail', pk=pk)
    else:
        form = TaskProgressForm(instance=task)
    
    return render(request, 'tasks/update_progress.html', {'form': form, 'task': task})