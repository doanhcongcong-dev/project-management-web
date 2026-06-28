from django.shortcuts import redirect
from django.contrib import messages
from .models import User2FA

def twofa_required(view_func):
    """Decorator yêu cầu user đã bật 2FA mới được truy cập"""
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            twofa, created = User2FA.objects.get_or_create(user=request.user)
            if not twofa.is_enabled:
                messages.warning(request, 'Vui lòng bật xác thực 2 yếu tố để truy cập tính năng này.')
                return redirect('security:2fa_setup')
        return view_func(request, *args, **kwargs)
    return wrapper