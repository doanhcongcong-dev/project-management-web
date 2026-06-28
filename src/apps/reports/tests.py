from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from apps.projects.models import Project
from apps.tasks.models import Task
from apps.risks.models import Risk

class ReportsViewTest(TestCase):
    def setUp(self):
        # Tạo user
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client = Client()
        self.client.login(username='testuser', password='12345')
        
        # Tạo dữ liệu mẫu
        self.project = Project.objects.create(
            name='Test Project',
            status='active',
            start_date='2025-01-01',
            end_date='2025-12-31'
        )
        self.task = Task.objects.create(
            title='Test Task',
            project=self.project,
            status='in_progress',
            due_date='2025-06-30'
        )
        self.risk = Risk.objects.create(
            project=self.project,
            title='Test Risk',
            description='Risk description',
            status='open'
        )

    def test_dashboard_view(self):
        response = self.client.get(reverse('reports:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Project')

    def test_project_report_view(self):
        response = self.client.get(reverse('reports:project_report'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Project')

    def test_task_report_view(self):
        response = self.client.get(reverse('reports:task_report'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Task')

    def test_risk_report_view(self):
        response = self.client.get(reverse('reports:risk_report'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Risk')