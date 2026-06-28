from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from .models import ChatRoom, Message
from .forms import MessageForm
from apps.projects.models import Project

@login_required
def room_list(request):
    """Danh sách các phòng chat của user"""
    rooms = request.user.chat_rooms.all().select_related('project')
    
    # Đếm tin nhắn chưa đọc
    for room in rooms:
        room.unread_count = Message.objects.filter(
            room=room
        ).exclude(
            sender=request.user
        ).filter(
            is_read=False
        ).count()
    
    context = {
        'rooms': rooms,
    }
    return render(request, 'chat/room_list.html', context)

@login_required
def room_detail(request, room_id):
    """Chi tiết phòng chat"""
    room = get_object_or_404(ChatRoom, id=room_id)
    
    # Kiểm tra user có trong phòng không
    if request.user not in room.members.all():
        messages.error(request, 'Bạn không có quyền truy cập phòng chat này.')
        return redirect('chat:room_list')
    
    # Lấy tin nhắn gần đây (phân trang)
    messages_qs = room.messages.all().select_related('sender')
    paginator = Paginator(messages_qs, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Đánh dấu tất cả tin nhắn đã đọc (khi vào phòng)
    Message.objects.filter(
        room=room
    ).exclude(
        sender=request.user
    ).update(
        is_read=True
    )
    
    context = {
        'room': room,
        'page_obj': page_obj,
        'project': room.project,
    }
    return render(request, 'chat/room_detail.html', context)

@login_required
def send_message(request, room_id):
    """Gửi tin nhắn (HTTP fallback khi không dùng WebSocket)"""
    room = get_object_or_404(ChatRoom, id=room_id)
    
    if request.user not in room.members.all():
        return JsonResponse({'error': 'Bạn không có quyền'}, status=403)
    
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.room = room
            message.sender = request.user
            message.save()
            return JsonResponse({
                'status': 'ok',
                'message': {
                    'id': message.id,
                    'sender': message.sender.username,
                    'content': message.content,
                    'timestamp': message.timestamp.strftime('%d/%m/%Y %H:%M')
                }
            })
    return JsonResponse({'error': 'Invalid request'}, status=400)