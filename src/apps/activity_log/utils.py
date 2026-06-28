def get_client_ip(request):
    """Lấy địa chỉ IP thực của client"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def get_user_agent(request):
    """Lấy User Agent từ request"""
    return request.META.get('HTTP_USER_AGENT', '')