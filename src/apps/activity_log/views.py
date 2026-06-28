from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from .models import ActivityLog
from .forms import ActivityLogFilterForm

@login_required
@staff_member_required  # Chỉ admin/staff mới xem được log
def list_view(request):
    """Danh sách nhật ký hoạt động"""
    logs = ActivityLog.objects.all().select_related('user')
    
    form = ActivityLogFilterForm(request.GET or None)
    if form.is_valid():
        # Lọc theo user
        user = form.cleaned_data.get('user')
        if user:
            logs = logs.filter(user=user)
        
        # Lọc theo action
        action = form.cleaned_data.get('action')
        if action:
            logs = logs.filter(action=action)
        
        # Lọc theo ngày
        date_from = form.cleaned_data.get('date_from')
        if date_from:
            logs = logs.filter(timestamp__date__gte=date_from)
        
        date_to = form.cleaned_data.get('date_to')
        if date_to:
            logs = logs.filter(timestamp__date__lte=date_to)
        
        # Tìm kiếm
        search = form.cleaned_data.get('search')
        if search:
            logs = logs.filter(
                Q(description__icontains=search) |
                Q(ip_address__icontains=search) |
                Q(user__username__icontains=search)
            )
    
    # Phân trang
    paginator = Paginator(logs, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'form': form,
    }
    return render(request, 'activity_log/list.html', context)

@login_required
@staff_member_required
def detail_view(request, pk):
    """Xem chi tiết một log"""
    log = get_object_or_404(ActivityLog, pk=pk)
    return render(request, 'activity_log/detail.html', {'log': log})