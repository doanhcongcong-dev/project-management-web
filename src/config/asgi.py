import os
from django.core.asgi import get_asgi_application
# from channels.routing import ProtocolTypeRouter, URLRouter  # nếu dùng Channels
# from apps.chat.routing import websocket_urlpatterns

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# application = ProtocolTypeRouter({
#     'http': get_asgi_application(),
#     'websocket': URLRouter(websocket_urlpatterns),
# })
application = get_asgi_application()  # tạm thời dùng ASGI cơ bản