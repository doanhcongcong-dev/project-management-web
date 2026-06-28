from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.models import User
from .models import EmployeeProfile
from .forms import EmployeeForm

@login_required
def list_view(request):
    """Danh sách nhân viên"""
    profiles = EmployeeProfile.objects.all().select_related('user')
    
    # Tìm kiếm
    search = request.GET.get('search')
    if search:
        profiles = profiles.filter(
            Q(user__username__icontains=search) |
            Q(user__first_name__icontains=search) |
            Q(user__last_name__icontains=search) |
            Q(employee_id__icontains=search) |
            Q(department__icontains=search) |
            Q(position__icontains=search)
        )
    
    # Lọc theo phòng ban
    department = request.GET.get('department')
    if department:
        profiles = profiles.filter(department=department)
    
    # Lọc theo trạng thái làm việc
    is_active = request.GET.get('is_active')
    if is_active in ['True', 'False']:
        profiles = profiles.filter(is_active=is_active == 'True')
    
    paginator = Paginator(profiles, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Lấy danh sách phòng ban để hiển thị filter
    departments = EmployeeProfile.objects.values_list('department', flat=True).distinct()
    
    context = {
        'page_obj': page_obj,
        'search_query': search,
        'selected_department': department,
        'selected_active': is_active,
        'departments': departments,
    }
    return render(request, 'employees/list.html', context)

@login_required
def detail_view(request, pk):
    """Chi tiết nhân viên"""
    profile = get_object_or_404(EmployeeProfile, pk=pk)
    context = {
        'profile': profile,
    }
    return render(request, 'employees/detail.html', context)

@login_required
def create_view(request):
    """Thêm nhân viên mới"""
    if not (request.user.is_staff or request.user.has_perm('employees.add_employeeprofile')):
        messages.error(request, 'Bạn không có quyền thêm nhân viên.')
        return redirect('employees:list')
    
    if request.method == 'POST':
        form = EmployeeForm(request.POST, request.FILES)
        if form.is_valid():
            profile = form.save()
            messages.success(request, f'Thêm nhân viên {profile.get_full_name()} thành công!')
            return redirect('employees:detail', pk=profile.pk)
    else:
        form = EmployeeForm()
    
    return render(request, 'employees/create.html', {'form': form})

@login_required
def edit_view(request, pk):
    """Chỉnh sửa nhân viên"""
    profile = get_object_or_404(EmployeeProfile, pk=pk)
    if not (request.user.is_staff or request.user.has_perm('employees.change_employeeprofile')):
        messages.error(request, 'Bạn không có quyền chỉnh sửa nhân viên này.')
        return redirect('employees:detail', pk=pk)
    
    if request.method == 'POST':
        form = EmployeeForm(request.POST, request.FILES, instance_profile=profile)
        if form.is_valid():
            profile = form.save()
            messages.success(request, f'Cập nhật nhân viên {profile.get_full_name()} thành công!')
            return redirect('employees:detail', pk=pk)
    else:
        form = EmployeeForm(instance_profile=profile)
    
    return render(request, 'employees/edit.html', {'form': form, 'profile': profile})

@login_required
def delete_view(request, pk):
    """Xóa nhân viên"""
    profile = get_object_or_404(EmployeeProfile, pk=pk)
    if not (request.user.is_staff or request.user.has_perm('employees.delete_employeeprofile')):
        messages.error(request, 'Bạn không có quyền xóa nhân viên này.')
        return redirect('employees:detail', pk=pk)
    
    if request.method == 'POST':
        user = profile.user
        profile.delete()
        user.delete()  # Xóa luôn User (cẩn thận, có thể ảnh hưởng)
        messages.success(request, 'Xóa nhân viên thành công!')
        return redirect('employees:list')
    
    return render(request, 'employees/confirm_delete.html', {'profile': profile})   