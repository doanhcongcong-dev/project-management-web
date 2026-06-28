from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Project
from .forms import ProjectForm
from apps.security.models import SecurityLog

@login_required
def list_view(request):
    """Danh sách dự án"""
    projects = Project.objects.all().select_related('manager')

    # Lọc theo trạng thái
    status = request.GET.get('status')
    if status:
        projects = projects.filter(status=status)

    # Tìm kiếm
    search = request.GET.get('search')
    if search:
        projects = projects.filter(
            Q(name__icontains=search) | Q(description__icontains=search)
        )

    # Nếu không phải admin, chỉ hiển thị dự án mà user tham gia hoặc quản lý
    if not request.user.is_staff:
        projects = projects.filter(
            Q(members=request.user) | Q(manager=request.user)
        )

    paginator = Paginator(projects, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'search_query': search,
        'status_filter': status,
    }
    return render(request, 'projects/list.html', context)


@login_required
def detail_view(request, pk):
    """Chi tiết dự án"""
    project = get_object_or_404(Project, pk=pk)

    # Kiểm tra quyền xem
    if not (request.user in project.members.all() or request.user == project.manager or request.user.is_staff):
        messages.error(request, 'Bạn không có quyền xem dự án này.')
        return redirect('projects:list')

    # Ghi log
    SecurityLog.objects.create(
        user=request.user,
        action='view',
        description=f'Xem dự án: {project.name}',
        object_id=project.id,
        content_type='project',
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT', '')
    )

    # Lấy danh sách task của dự án
    tasks = project.tasks.all().order_by('-created_at')[:10]

    context = {
        'project': project,
        'tasks': tasks,
        'progress': project.get_progress(),
    }
    return render(request, 'projects/detail.html', context)


@login_required
def create_view(request):
    """Tạo dự án mới"""
    if not (request.user.is_staff or request.user.has_perm('projects.add_project')):
        messages.error(request, 'Bạn không có quyền tạo dự án.')
        return redirect('projects:list')

    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save()
            # Ghi log
            SecurityLog.objects.create(
                user=request.user,
                action='create',
                description=f'Tạo dự án: {project.name}',
                object_id=project.id,
                content_type='project',
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            messages.success(request, 'Tạo dự án thành công!')
            return redirect('projects:detail', pk=project.pk)
    else:
        form = ProjectForm()

    return render(request, 'projects/create.html', {'form': form})


@login_required
def edit_view(request, pk):
    """Chỉnh sửa dự án"""
    project = get_object_or_404(Project, pk=pk)

    if not (request.user == project.manager or request.user.is_staff or request.user.has_perm('projects.change_project')):
        messages.error(request, 'Bạn không có quyền chỉnh sửa dự án này.')
        return redirect('projects:detail', pk=pk)

    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            SecurityLog.objects.create(
                user=request.user,
                action='update',
                description=f'Cập nhật dự án: {project.name}',
                object_id=project.id,
                content_type='project',
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            messages.success(request, 'Cập nhật dự án thành công!')
            return redirect('projects:detail', pk=pk)
    else:
        form = ProjectForm(instance=project)

    return render(request, 'projects/edit.html', {'form': form, 'project': project})


@login_required
def delete_view(request, pk):
    """Xóa dự án"""
    project = get_object_or_404(Project, pk=pk)

    if not (request.user == project.manager or request.user.is_staff or request.user.has_perm('projects.delete_project')):
        messages.error(request, 'Bạn không có quyền xóa dự án này.')
        return redirect('projects:detail', pk=pk)

    if request.method == 'POST':
        name = project.name
        project.delete()
        SecurityLog.objects.create(
            user=request.user,
            action='delete',
            description=f'Xóa dự án: {name}',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        messages.success(request, 'Dự án đã được xóa.')
        return redirect('projects:list')

    return render(request, 'projects/confirm_delete.html', {'project': project})