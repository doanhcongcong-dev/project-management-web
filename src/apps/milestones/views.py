from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from .models import Milestone
from .forms import MilestoneForm
from apps.projects.models import Project

@login_required
def list_view(request):
    """Danh sách cột mốc (có lọc theo dự án)"""
    milestones = Milestone.objects.all().select_related('project', 'created_by')
    
    # Lọc theo dự án
    project_id = request.GET.get('project')
    if project_id:
        milestones = milestones.filter(project_id=project_id)
    
    # Lọc theo trạng thái
    status = request.GET.get('status')
    if status:
        milestones = milestones.filter(status=status)
    
    # Tìm kiếm
    search = request.GET.get('search')
    if search:
        milestones = milestones.filter(
            Q(name__icontains=search) | Q(description__icontains=search)
        )
    
    paginator = Paginator(milestones, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    projects = Project.objects.filter(status__in=['active', 'planning'])
    
    context = {
        'page_obj': page_obj,
        'projects': projects,
        'selected_project': project_id,
        'selected_status': status,
        'search_query': search,
    }
    return render(request, 'milestones/list.html', context)

@login_required
def detail_view(request, pk):
    """Chi tiết cột mốc"""
    milestone = get_object_or_404(Milestone, pk=pk)
    tasks = milestone.tasks.all()
    progress = milestone.get_progress()
    
    context = {
        'milestone': milestone,
        'tasks': tasks,
        'progress': progress,
    }
    return render(request, 'milestones/detail.html', context)

@login_required
def create_view(request):
    """Tạo cột mốc mới"""
    if not (request.user.is_staff or request.user.has_perm('milestones.add_milestone')):
        messages.error(request, 'Bạn không có quyền tạo cột mốc.')
        return redirect('milestones:list')
    
    if request.method == 'POST':
        form = MilestoneForm(request.POST, user=request.user)
        if form.is_valid():
            milestone = form.save(commit=False)
            milestone.created_by = request.user
            milestone.save()
            form.save_m2m()  # Lưu tasks (ManyToMany)
            messages.success(request, 'Tạo cột mốc thành công!')
            return redirect('milestones:detail', pk=milestone.pk)
    else:
        initial = {}
        project_id = request.GET.get('project')
        if project_id:
            initial['project'] = project_id
        form = MilestoneForm(user=request.user, initial=initial)
    
    return render(request, 'milestones/create.html', {'form': form})

@login_required
def edit_view(request, pk):
    """Chỉnh sửa cột mốc"""
    milestone = get_object_or_404(Milestone, pk=pk)
    if not (request.user == milestone.created_by or request.user.is_staff or request.user.has_perm('milestones.change_milestone')):
        messages.error(request, 'Bạn không có quyền chỉnh sửa cột mốc này.')
        return redirect('milestones:detail', pk=pk)
    
    if request.method == 'POST':
        form = MilestoneForm(request.POST, instance=milestone, user=request.user)
        if form.is_valid():
            milestone = form.save()
            milestone.update_status()  # Cập nhật trạng thái tự động
            messages.success(request, 'Cập nhật cột mốc thành công!')
            return redirect('milestones:detail', pk=pk)
    else:
        form = MilestoneForm(instance=milestone, user=request.user)
    
    return render(request, 'milestones/edit.html', {'form': form, 'milestone': milestone})

@login_required
def delete_view(request, pk):
    """Xóa cột mốc"""
    milestone = get_object_or_404(Milestone, pk=pk)
    if not (request.user == milestone.created_by or request.user.is_staff or request.user.has_perm('milestones.delete_milestone')):
        messages.error(request, 'Bạn không có quyền xóa cột mốc này.')
        return redirect('milestones:detail', pk=pk)
    
    if request.method == 'POST':
        milestone.delete()
        messages.success(request, 'Cột mốc đã được xóa.')
        return redirect('milestones:list')
    
    return render(request, 'milestones/confirm_delete.html', {'milestone': milestone})

@login_required
def update_progress(request, pk):
    """Cập nhật tiến độ (tự động, chỉ dành cho admin)"""
    milestone = get_object_or_404(Milestone, pk=pk)
    if request.user.is_staff or request.user == milestone.created_by:
        milestone.update_status()
        messages.success(request, 'Đã cập nhật tiến độ cột mốc.')
    else:
        messages.error(request, 'Bạn không có quyền cập nhật tiến độ.')
    return redirect('milestones:detail', pk=pk)