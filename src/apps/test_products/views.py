from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import TestProduct
from .forms import TestProductForm
from apps.projects.models import Project

@login_required
def list_view(request):
    """Danh sách sản phẩm thử nghiệm"""
    queryset = TestProduct.objects.all()
    
    # Lọc theo project
    project_id = request.GET.get('project')
    if project_id:
        queryset = queryset.filter(project_id=project_id)
    
    # Lọc theo kết quả
    result = request.GET.get('result')
    if result:
        queryset = queryset.filter(result=result)
    
    # Tìm kiếm
    search = request.GET.get('search')
    if search:
        queryset = queryset.filter(
            Q(name__icontains=search) | 
            Q(version__icontains=search) |
            Q(notes__icontains=search)
        )
    
    # Phân trang
    paginator = Paginator(queryset, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Lấy danh sách project để hiển thị filter
    projects = Project.objects.filter(status__in=['active', 'planning'])
    
    context = {
        'page_obj': page_obj,
        'projects': projects,
        'selected_project': project_id,
        'selected_result': result,
        'search_query': search,
    }
    return render(request, 'test_products/list.html', context)

@login_required
def detail_view(request, pk):
    """Chi tiết sản phẩm thử nghiệm"""
    product = get_object_or_404(TestProduct, pk=pk)
    return render(request, 'test_products/detail.html', {'product': product})

@login_required
def create_view(request):
    """Thêm mới sản phẩm thử nghiệm"""
    if not request.user.is_staff and not request.user.has_perm('test_products.add_testproduct'):
        messages.error(request, 'Bạn không có quyền thêm mới.')
        return redirect('test_products:list')
    
    if request.method == 'POST':
        form = TestProductForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Thêm sản phẩm thử nghiệm thành công!')
            return redirect('test_products:list')
    else:
        # Pre-fill với project nếu có param
        initial = {}
        project_id = request.GET.get('project')
        if project_id:
            initial['project'] = project_id
        form = TestProductForm(initial=initial)
    
    return render(request, 'test_products/create.html', {'form': form})

@login_required
def edit_view(request, pk):
    """Chỉnh sửa sản phẩm thử nghiệm"""
    product = get_object_or_404(TestProduct, pk=pk)
    
    if not request.user.is_staff and not request.user.has_perm('test_products.change_testproduct'):
        messages.error(request, 'Bạn không có quyền chỉnh sửa.')
        return redirect('test_products:detail', pk=pk)
    
    if request.method == 'POST':
        form = TestProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cập nhật sản phẩm thử nghiệm thành công!')
            return redirect('test_products:detail', pk=pk)
    else:
        form = TestProductForm(instance=product)
    
    return render(request, 'test_products/edit.html', {'form': form, 'product': product})

@login_required
def delete_view(request, pk):
    """Xóa sản phẩm thử nghiệm"""
    product = get_object_or_404(TestProduct, pk=pk)
    
    if not request.user.is_staff and not request.user.has_perm('test_products.delete_testproduct'):
        messages.error(request, 'Bạn không có quyền xóa.')
        return redirect('test_products:list')
    
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Xóa sản phẩm thử nghiệm thành công!')
        return redirect('test_products:list')
    
    return render(request, 'test_products/confirm_delete.html', {'product': product})