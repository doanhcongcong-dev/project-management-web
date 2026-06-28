from django import forms
from .models import Milestone
from apps.projects.models import Project
from apps.tasks.models import Task

class MilestoneForm(forms.ModelForm):
    class Meta:
        model = Milestone
        fields = ['project', 'name', 'description', 'due_date', 'status', 'tasks']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4}),
            'tasks': forms.SelectMultiple(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        # Giới hạn project chỉ những dự án user tham gia hoặc quản lý
        if user and not user.is_staff:
            self.fields['project'].queryset = Project.objects.filter(
                models.Q(members=user) | models.Q(manager=user)
            ).distinct()
        # Giới hạn tasks chỉ những task thuộc project đã chọn
        if 'project' in self.data and self.data.get('project'):
            project_id = self.data.get('project')
            self.fields['tasks'].queryset = Task.objects.filter(project_id=project_id)
        elif self.instance and self.instance.pk and self.instance.project:
            self.fields['tasks'].queryset = Task.objects.filter(project=self.instance.project)
        else:
            self.fields['tasks'].queryset = Task.objects.none()