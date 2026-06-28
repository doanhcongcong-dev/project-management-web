from django.utils.deprecation import MiddlewareMixin
from .models import ActivityLog
from .utils import get_client_ip, get_user_agent

class ActivityLogMiddleware(MiddlewareMixin):
    """Middleware tự động ghi log mọi request (có thể bật/tắt)"""

    # Danh sách URL không cần ghi log (ví dụ: static, media)
    EXCLUDED_PATHS = ['/static/', '/media/', '/admin/jsi18n/']

    def process_request(self, request):
        # Bỏ qua nếu không phải user đã đăng nhập hoặc URL bị loại trừ
        if not request.user.is_authenticated:
            return

        path = request.path
        for excluded in self.EXCLUDED_PATHS:
            if path.startswith(excluded):
                return

        # Chỉ ghi log cho các method quan trọng
        if request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            action_map = {
                'POST': 'create',
                'PUT': 'update',
                'PATCH': 'update',
                'DELETE': 'delete',
            }
            action = action_map.get(request.method, 'other')
            description = f"{request.method} {path}"

            # Ghi log bất đồng bộ (có thể dùng Celery để tối ưu)
            ActivityLog.objects.create(
                user=request.user,
                action=action,
                description=description,
                ip_address=get_client_ip(request),
                user_agent=get_user_agent(request),
                url=request.build_absolute_uri(),
                method=request.method,
            )