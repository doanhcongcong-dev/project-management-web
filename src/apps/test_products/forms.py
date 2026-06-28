from django import forms
from .models import TestProduct
from apps.projects.models import Project
from django.contrib.auth.models import User

class TestProductForm(forms.ModelForm):
    class Meta:
        model = TestProduct
        fields = ['project', 'name', 'version', 'environment', 'result', 'tester', 'test_date', 'notes']
        widgets = {
            'test_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Giới hạn lựa chọn project (chỉ những project đang active)
        self.fields['project'].queryset = Project.objects.filter(
            status__in=['active', 'planning']
        )
        # Giới hạn tester là nhân viên (có thể custom)
        self.fields['tester'].queryset = User.objects.filter(is_active=True)