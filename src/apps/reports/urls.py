from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('projects/', views.project_report, name='project_report'),
    path('tasks/', views.task_report, name='task_report'),
    path('employees/', views.employee_report, name='employee_report'),
    path('chart-data/', views.chart_data, name='chart_data'),
]