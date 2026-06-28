from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from .models import Risk, RiskCategory, RiskHistory
from .forms import RiskForm
from apps.security.models import SecurityLog
from apps.projects.models import Project

@login_required
def list_view(request):
    """Danh sách rủi ro (có lọc)"""
    risks = Risk.objects.all().select_related('project', 'category', 'assigned_to', 'created_by')
    
    # Lọc theo dự án
    project_id = request.GET.get('project')
    if project_id:
        risks = risks.filter(project_id=project_id)
    
    # Lọc theo danh mục
    category_id = request.GET.get('category')
    if category_id:
        risks = risks.filter(category_id=category_id)
    
    # Lọc theo trạng thái
    status = request.GET.get('status')
    if status:
        risks = risks.filter(status=status)
    
    # Lọc theo người phụ trách
    assigned = request.GET.get('assigned')
    if assigned:
        risks = risks.filter(assigned_to_id=assigned)
    
    # Tìm kiếm
    search = request.GET.get('search')
    if search:
        risks = risks.filter(
            Q(title__icontains=search) |
            Q(description__icontains=search)
        )
    
    # Sắp xếp
    order_by = request.GET.get('order_by', '-created_at')
    risks = risks.order_by(order_by)
    
    paginator = Paginator(risks, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Dữ liệu cho filter
    projects = Project.objects.filter(status__in=['active', 'planning'])
    categories = RiskCategory.objects.all()
    users = User.objects.filter(is_active=True)
    
    context = {
        'page_obj': page_obj,
        'projects': projects,
        'categories': categories,
        'users': users,
        'selected_project': project_id,
        'selected_category': category_id,
        'selected_status': status,
        'selected_assigned': assigned,
        'search_query': search,
        'order_by': order_by,
    }
    return render(request, 'risks/list.html', context)

@login_required
def detail_view(request, pk):
    """Chi tiết rủi ro"""
    risk = get_object_or_404(Risk, pk=pk)
    # Ghi log view (tùy chọn)
    SecurityLog.objects.create(
        user=request.user,
        action='view',
        description=f'Xem rủi ro: {risk.title}',
        object_id=risk.id,
        content_type='risk',
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT', '')
    )
    return render(request, 'risks/detail.html', {'risk': risk})

@login_required
def create_view(request):
    """Thêm rủi ro mới"""
    if not (request.user.is_staff or request.user.has_perm('risks.add_risk')):
        messages.error(request, 'Bạn không có quyền thêm rủi ro.')
        return redirect('risks:list')
    
    if request.method == 'POST':
        form = RiskForm(request.POST, user=request.user)
        if form.is_valid():
            risk = form.save(commit=False)
            risk.created_by = request.user
            risk.save()
            # Ghi log
            SecurityLog.objects.create(
                user=request.user,
                action='create',
                description=f'Tạo rủi ro: {risk.title}',
                object_id=risk.id,
                content_type='risk',
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            messages.success(request, 'Tạo rủi ro thành công!')
            return redirect('risks:detail', pk=risk.pk)
    else:
        initial = {}
        project_id = request.GET.get('project')
        if project_id:
            initial['project'] = project_id
        form = RiskForm(user=request.user, initial=initial)
    
    return render(request, 'risks/create.html', {'form': form})

@login_required
def edit_view(request, pk):
    """Chỉnh sửa rủi ro"""
    risk = get_object_or_404(Risk, pk=pk)
    if not (request.user == risk.created_by or request.user.is_staff or request.user.has_perm('risks.change_risk')):
        messages.error(request, 'Bạn không có quyền chỉnh sửa rủi ro này.')
        return redirect('risks:detail', pk=pk)
    
    if request.method == 'POST':
        form = RiskForm(request.POST, instance=risk, user=request.user)
        if form.is_valid():
            old_status = risk.status
            risk = form.save()
            # Nếu status thay đổi và chuyển sang closed, cập nhật closed_at
            if risk.status == 'closed' and old_status != 'closed':
                risk.closed_at = timezone.now()
                risk.save()
            # Ghi log
            SecurityLog.objects.create(
                user=request.user,
                action='update',
                description=f'Cập nhật rủi ro: {risk.title}',
                object_id=risk.id,
                content_type='risk',
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            messages.success(request, 'Cập nhật rủi ro thành công!')
            return redirect('risks:detail', pk=pk)
    else:
        form = RiskForm(instance=risk, user=request.user)
    
    return render(request, 'risks/edit.html', {'form': form, 'risk': risk})

@login_required
def delete_view(request, pk):
    """Xóa rủi ro"""
    risk = get_object_or_404(Risk, pk=pk)
    if not (request.user == risk.created_by or request.user.is_staff or request.user.has_perm('risks.delete_risk')):
        messages.error(request, 'Bạn không có quyền xóa rủi ro này.')
        return redirect('risks:detail', pk=pk)
    
    if request.method == 'POST':
        title = risk.title
        risk.delete()
        SecurityLog.objects.create(
            user=request.user,
            action='delete',
            description=f'Xóa rủi ro: {title}',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        messages.success(request, 'Rủi ro đã được xóa.')
        return redirect('risks:list')
    
    return render(request, 'risks/confirm_delete.html', {'risk': risk})