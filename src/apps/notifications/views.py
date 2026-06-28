from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from .models import Notification
from .forms import NotificationFilterForm

@login_required
def list_view(request):
    """Danh sách thông báo của user hiện tại"""
    notifications = Notification.objects.filter(recipient=request.user)
    
    # Lọc
    form = NotificationFilterForm(request.GET or None)
    if form.is_valid():
        is_read = form.cleaned_data.get('is_read')
        if is_read == 'True':
            notifications = notifications.filter(is_read=True)
        elif is_read == 'False':
            notifications = notifications.filter(is_read=False)
        
        date_from = form.cleaned_data.get('date_from')
        if date_from:
            notifications = notifications.filter(created_at__date__gte=date_from)
        
        date_to = form.cleaned_data.get('date_to')
        if date_to:
            notifications = notifications.filter(created_at__date__lte=date_to)
    
    # Phân trang
    paginator = Paginator(notifications, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Đếm chưa đọc
    unread_count = Notification.objects.filter(recipient=request.user, is_read=False).count()
    
    context = {
        'page_obj': page_obj,
        'form': form,
        'unread_count': unread_count,
    }
    return render(request, 'notifications/list.html', context)

@login_required
def mark_as_read(request, pk):
    """Đánh dấu một thông báo đã đọc"""
    notification = get_object_or_404(Notification, pk=pk, recipient=request.user)
    notification.mark_as_read()
    return JsonResponse({'status': 'ok'})

@login_required
def mark_all_read(request):
    """Đánh dấu tất cả đã đọc"""
    Notification.objects.filter(recipient=request.user, is_read=False).update(
        is_read=True,
        read_at=timezone.now()
    )
    messages.success(request, 'Đã đánh dấu tất cả thông báo đã đọc.')
    return redirect('notifications:list')

@login_required
def detail_view(request, pk):
    """Xem chi tiết thông báo (đánh dấu đã đọc ngay khi xem)"""
    notification = get_object_or_404(Notification, pk=pk, recipient=request.user)
    notification.mark_as_read()
    return render(request, 'notifications/detail.html', {'notification': notification})

@login_required
def delete_view(request, pk):
    """Xóa một thông báo"""
    notification = get_object_or_404(Notification, pk=pk, recipient=request.user)
    if request.method == 'POST':
        notification.delete()
        messages.success(request, 'Thông báo đã được xóa.')
        return redirect('notifications:list')
    return render(request, 'notifications/confirm_delete.html', {'notification': notification})

@login_required
def get_unread_count(request):
    """API trả về số thông báo chưa đọc (dùng cho AJAX)"""
    count = Notification.objects.filter(recipient=request.user, is_read=False).count()
    return JsonResponse({'unread_count': count})

@login_required
def get_latest_notifications(request):
    """API trả về 5 thông báo mới nhất (dùng cho dropdown)"""
    notifications = Notification.objects.filter(
        recipient=request.user
    ).order_by('-created_at')[:5]
    data = [
        {
            'id': n.id,
            'title': n.title,
            'message': n.message[:50] + '...' if len(n.message) > 50 else n.message,
            'link': n.link,
            'is_read': n.is_read,
            'created_at': n.created_at.strftime('%d/%m/%Y %H:%M')
        }
        for n in notifications
    ]
    unread_count = Notification.objects.filter(recipient=request.user, is_read=False).count()
    return JsonResponse({
        'notifications': data,
        'unread_count': unread_count
    })