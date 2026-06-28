from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.models import User
from .models import Document
from .forms import DocumentForm
from apps.projects.models import Project
from apps.security.models import SecurityLog

@login_required
def list_view(request):
    """Danh sách tài liệu"""
    documents = Document.objects.all().select_related('project', 'uploaded_by')
    
    # Lọc theo dự án
    project_id = request.GET.get('project')
    if project_id:
        documents = documents.filter(project_id=project_id)
    
    # Lọc theo loại tài liệu
    doc_type = request.GET.get('type')
    if doc_type:
        documents = documents.filter(document_type=doc_type)
    
    # Tìm kiếm
    search = request.GET.get('search')
    if search:
        documents = documents.filter(
            Q(name__icontains=search) |
            Q(description__icontains=search) |
            Q(version__icontains=search)
        )
    
    # Nếu user không phải staff, chỉ hiển thị tài liệu của dự án họ tham gia
    if not request.user.is_staff:
        user_projects = request.user.projects.all()
        documents = documents.filter(project__in=user_projects)
    
    paginator = Paginator(documents, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Lấy danh sách project để hiển thị filter
    projects = Project.objects.all()
    if not request.user.is_staff:
        projects = request.user.projects.all()
    
    context = {
        'page_obj': page_obj,
        'projects': projects,
        'document_types': Document.DOCUMENT_TYPES,
        'selected_project': project_id,
        'selected_type': doc_type,
        'search_query': search,
    }
    return render(request, 'documents/list.html', context)

@login_required
def detail_view(request, pk):
    """Chi tiết tài liệu"""
    document = get_object_or_404(Document, pk=pk)
    # Kiểm tra quyền
    if not request.user.is_staff and not request.user.projects.filter(id=document.project.id).exists():
        messages.error(request, 'Bạn không có quyền truy cập tài liệu này.')
        return redirect('documents:list')
    
    # Ghi log view
    SecurityLog.objects.create(
        user=request.user,
        action='view',
        description=f'Xem tài liệu: {document.name}',
        object_id=document.id,
        content_type='document',
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT', '')
    )
    return render(request, 'documents/detail.html', {'document': document})

@login_required
def create_view(request):
    """Tải lên tài liệu mới"""
    if not (request.user.is_staff or request.user.has_perm('documents.add_document')):
        messages.error(request, 'Bạn không có quyền tải lên tài liệu.')
        return redirect('documents:list')
    
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            document = form.save(commit=False)
            document.uploaded_by = request.user
            document.save()
            # Ghi log
            SecurityLog.objects.create(
                user=request.user,
                action='create',
                description=f'Tải lên tài liệu: {document.name}',
                object_id=document.id,
                content_type='document',
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            messages.success(request, 'Tải lên tài liệu thành công!')
            return redirect('documents:detail', pk=document.pk)
    else:
        initial = {}
        project_id = request.GET.get('project')
        if project_id:
            initial['project'] = project_id
        form = DocumentForm(user=request.user, initial=initial)
    
    return render(request, 'documents/create.html', {'form': form})

@login_required
def edit_view(request, pk):
    """Chỉnh sửa thông tin tài liệu"""
    document = get_object_or_404(Document, pk=pk)
    if not (request.user == document.uploaded_by or request.user.is_staff or request.user.has_perm('documents.change_document')):
        messages.error(request, 'Bạn không có quyền chỉnh sửa tài liệu này.')
        return redirect('documents:detail', pk=pk)
    
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES, instance=document, user=request.user)
        if form.is_valid():
            document = form.save()
            # Ghi log
            SecurityLog.objects.create(
                user=request.user,
                action='update',
                description=f'Cập nhật tài liệu: {document.name}',
                object_id=document.id,
                content_type='document',
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            messages.success(request, 'Cập nhật tài liệu thành công!')
            return redirect('documents:detail', pk=pk)
    else:
        form = DocumentForm(instance=document, user=request.user)
    
    return render(request, 'documents/edit.html', {'form': form, 'document': document})

@login_required
def delete_view(request, pk):
    """Xóa tài liệu"""
    document = get_object_or_404(Document, pk=pk)
    if not (request.user == document.uploaded_by or request.user.is_staff or request.user.has_perm('documents.delete_document')):
        messages.error(request, 'Bạn không có quyền xóa tài liệu này.')
        return redirect('documents:detail', pk=pk)
    
    if request.method == 'POST':
        name = document.name
        document.delete()
        SecurityLog.objects.create(
            user=request.user,
            action='delete',
            description=f'Xóa tài liệu: {name}',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        messages.success(request, 'Tài liệu đã được xóa.')
        return redirect('documents:list')
    
    return render(request, 'documents/confirm_delete.html', {'document': document})

@login_required
def download_view(request, pk):
    """Tải file tài liệu"""
    document = get_object_or_404(Document, pk=pk)
    if not request.user.is_staff and not request.user.projects.filter(id=document.project.id).exists():
        messages.error(request, 'Bạn không có quyền tải tài liệu này.')
        return redirect('documents:list')
    
    # Ghi log
    SecurityLog.objects.create(
        user=request.user,
        action='view',
        description=f'Tải tài liệu: {document.name}',
        object_id=document.id,
        content_type='document',
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT', '')
    )
    
    if document.file:
        response = HttpResponse(document.file, content_type='application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename="{document.name}{document.get_file_extension()}"'
        return response
    return HttpResponse('File không tồn tại', status=404)