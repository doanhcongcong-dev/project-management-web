from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from .models import WazuhAlert
from .tasks import sync_wazuh_alerts

@login_required
def alert_list(request):
    """Danh sách cảnh báo"""
    queryset = WazuhAlert.objects.all()

    # Lọc theo level
    level = request.GET.get('level')
    if level:
        queryset = queryset.filter(level=level)

    # Lọc theo trạng thái
    acknowledged = request.GET.get('acknowledged')
    if acknowledged == 'yes':
        queryset = queryset.filter(is_acknowledged=True)
    elif acknowledged == 'no':
        queryset = queryset.filter(is_acknowledged=False)

    # Tìm kiếm
    search = request.GET.get('search')
    if search:
        queryset = queryset.filter(
            Q(rule_description__icontains=search) |
            Q(source_ip__icontains=search) |
            Q(agent_name__icontains=search)
        )

    # Phân trang
    paginator = Paginator(queryset, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Thống kê
    total_critical = queryset.filter(level__gte=10).count()
    total_high = queryset.filter(level__gte=7, level__lt=10).count()
    total_medium = queryset.filter(level__gte=4, level__lt=7).count()
    total_low = queryset.filter(level__lt=4).count()

    context = {
        'page_obj': page_obj,
        'search_query': search,
        'selected_level': level,
        'selected_acknowledged': acknowledged,
        'total_critical': total_critical,
        'total_high': total_high,
        'total_medium': total_medium,
        'total_low': total_low,
    }
    return render(request, 'wazuh/alert_list.html', context)

@login_required
def alert_detail(request, pk):
    """Chi tiết cảnh báo"""
    alert = get_object_or_404(WazuhAlert, pk=pk)
    return render(request, 'wazuh/alert_detail.html', {'alert': alert})

@login_required
def acknowledge_alert(request, pk):
    """Xác nhận cảnh báo"""
    alert = get_object_or_404(WazuhAlert, pk=pk)
    if request.method == 'POST':
        alert.is_acknowledged = True
        alert.acknowledged_by = request.user
        alert.acknowledged_at = timezone.now()
        alert.save()
        messages.success(request, 'Đã xác nhận cảnh báo thành công.')
        return redirect('wazuh_integration:alert_detail', pk=alert.pk)
    return redirect('wazuh_integration:alert_detail', pk=alert.pk)

@login_required
def sync_alerts_view(request):
    """Kích hoạt đồng bộ alerts (chỉ admin)"""
    if not request.user.is_staff:
        messages.error(request, 'Bạn không có quyền thực hiện hành động này.')
        return redirect('wazuh_integration:alert_list')
    
    # Chạy task đồng bộ (bất đồng bộ)
    sync_wazuh_alerts.delay()
    messages.success(request, 'Đã bắt đầu đồng bộ alerts. Vui lòng kiểm tra sau vài giây.')
    return redirect('wazuh_integration:alert_list')