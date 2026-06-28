from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('apps.users.urls')),
    path('projects/', include('apps.projects.urls')),
    path('tasks/', include('apps.tasks.urls')),
    path('employees/', include('apps.employees.urls')),
    path('milestones/', include('apps.milestones.urls')),
    path('test-products/', include('apps.test_products.urls')),
    path('notifications/', include('apps.notifications.urls')),
    path('reports/', include('apps.reports.urls')),
    path('dashboard/', include('apps.dashboard.urls')),
    path('security/', include('apps.security.urls')),
    path('wazuh/', include('apps.wazuh_integration.urls')),
    path('documents/', include('apps.documents.urls')),
    path('risks/', include('apps.risks.urls')),
    path('chat/', include('apps.chat.urls')),
    path('activity-log/', include('apps.activity_log.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)