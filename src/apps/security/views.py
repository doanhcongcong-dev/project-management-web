import pyotp
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator
from django.utils import timezone
from .models import SecurityLog, User2FA
from .forms import OTPVerificationForm, Enable2FAForm
from .utils import encrypt_data, decrypt_data
from apps.users.models import UserProfile  # để demo mã hóa

# ---- Logs ----
@staff_member_required
def log_list(request):
    """Hiển thị log bảo mật (chỉ admin)"""
    logs = SecurityLog.objects.all().select_related('user')
    
    # Lọc theo user
    user_id = request.GET.get('user')
    if user_id:
        logs = logs.filter(user_id=user_id)
    
    # Lọc theo action
    action = request.GET.get('action')
    if action:
        logs = logs.filter(action=action)
    
    paginator = Paginator(logs, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Lấy danh sách user và action để hiển thị filter
    from django.contrib.auth.models import User
    users = User.objects.filter(is_active=True)
    actions = SecurityLog.ACTION_CHOICES
    
    context = {
        'page_obj': page_obj,
        'users': users,
        'actions': actions,
        'selected_user': user_id,
        'selected_action': action,
    }
    return render(request, 'security/logs.html', context)

# ---- 2FA ----
@login_required
def setup_2fa(request):
    """Bật 2FA cho user hiện tại"""
    twofa, created = User2FA.objects.get_or_create(user=request.user)
    
    if twofa.is_enabled:
        messages.info(request, '2FA đã được bật.')
        return redirect('security:2fa_verify')
    
    if request.method == 'POST':
        form = Enable2FAForm(request.POST)
        if form.is_valid():
            # Tạo secret nếu chưa có
            if not twofa.secret:
                twofa.secret = pyotp.random_base32()
            twofa.is_enabled = True
            twofa.save()
            
            # Ghi log
            SecurityLog.objects.create(
                user=request.user,
                action='2fa_enable',
                description='Bật xác thực 2 yếu tố',
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            messages.success(request, '2FA đã được bật thành công!')
            return redirect('security:2fa_verify')
    else:
        form = Enable2FAForm()
    
    # Tạo URI để hiển thị QR code (dùng thư viện pyotp)
    if twofa.secret:
        totp = pyotp.TOTP(twofa.secret)
        provisioning_uri = totp.provisioning_uri(request.user.email, issuer_name="Project Management")
    else:
        # Tạo secret mới để hiển thị
        temp_secret = pyotp.random_base32()
        totp = pyotp.TOTP(temp_secret)
        provisioning_uri = totp.provisioning_uri(request.user.email, issuer_name="Project Management")
        # Lưu tạm vào session để dùng khi xác thực (hoặc lưu vào model)
        request.session['temp_2fa_secret'] = temp_secret
    
    context = {
        'form': form,
        'provisioning_uri': provisioning_uri,
        'secret': twofa.secret if twofa.secret else temp_secret,
    }
    return render(request, 'security/2fa_setup.html', context)


@login_required
def verify_2fa(request):
    """Xác thực OTP sau khi bật 2FA"""
    twofa = get_object_or_404(User2FA, user=request.user)
    
    if not twofa.is_enabled:
        messages.warning(request, 'Bạn chưa bật 2FA.')
        return redirect('security:2fa_setup')
    
    if request.method == 'POST':
        form = OTPVerificationForm(request.POST)
        if form.is_valid():
            otp = form.cleaned_data['otp_code']
            totp = pyotp.TOTP(twofa.secret)
            if totp.verify(otp):
                # Lưu vào session để biết user đã xác thực (có thể dùng cho các view yêu cầu 2FA)
                request.session['2fa_verified'] = True
                messages.success(request, 'Xác thực 2FA thành công!')
                return redirect('dashboard:index')
            else:
                messages.error(request, 'Mã OTP không hợp lệ.')
    else:
        form = OTPVerificationForm()
    
    return render(request, 'security/2fa_verify.html', {'form': form})


@login_required
def disable_2fa(request):
    """Tắt 2FA"""
    twofa = get_object_or_404(User2FA, user=request.user)
    if request.method == 'POST':
        twofa.is_enabled = False
        twofa.save()
        SecurityLog.objects.create(
            user=request.user,
            action='2fa_disable',
            description='Tắt xác thực 2 yếu tố',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        messages.success(request, 'Đã tắt 2FA.')
        if '2fa_verified' in request.session:
            del request.session['2fa_verified']
        return redirect('dashboard:index')
    return render(request, 'security/2fa_disable_confirm.html')


# ---- Demo mã hóa ----
@login_required
def encrypt_demo(request):
    """Demo mã hóa/giải mã dữ liệu"""
    encrypted_data = None
    decrypted_data = None
    original_text = ""

    if request.method == 'POST':
        original_text = request.POST.get('text', '')
        if 'encrypt' in request.POST:
            encrypted_data = encrypt_data(original_text)
        elif 'decrypt' in request.POST:
            encrypted_text = request.POST.get('encrypted_text', '')
            decrypted_data = decrypt_data(encrypted_text)
            if decrypted_data == encrypted_text:  # nếu không giải mã được
                messages.warning(request, 'Không thể giải mã, dữ liệu có thể không hợp lệ.')
    
    context = {
        'encrypted_data': encrypted_data,
        'decrypted_data': decrypted_data,
        'original_text': original_text,
    }
    return render(request, 'security/encrypt_demo.html', context)