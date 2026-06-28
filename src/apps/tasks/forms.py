from django import forms
from .models import Task
from apps.projects.models import Project
from django.contrib.auth.models import User

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'project', 'assigned_to', 'priority', 'status', 'due_date', 'progress']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4}),
            'assigned_to': forms.SelectMultiple(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        # Chỉ hiển thị các dự án mà user tham gia (hoặc là manager)
        if user:
            self.fields['project'].queryset = Project.objects.filter(
                models.Q(members=user) | models.Q(manager=user)
            ).distinct()
        # Giới hạn assigned_to là những user active
        self.fields['assigned_to'].queryset = User.objects.filter(is_active=True)

class TaskProgressForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['progress', 'status']
        widgets = {
            'progress': forms.NumberInput(attrs={'min': 0, 'max': 100}),
        }