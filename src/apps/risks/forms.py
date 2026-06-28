from django import forms
from .models import Risk, RiskCategory

class RiskForm(forms.ModelForm):
    class Meta:
        model = Risk
        fields = [
            'project', 'category', 'title', 'description',
            'probability', 'impact', 'status', 'mitigation_plan',
            'assigned_to'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
            'mitigation_plan': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        # Giới hạn project theo quyền (nếu cần)
        if user and not user.is_staff:
            self.fields['project'].queryset = user.projects.all()
        # Giới hạn assigned_to chỉ active user
        self.fields['assigned_to'].queryset = self.fields['assigned_to'].queryset.filter(is_active=True)
        self.fields['category'].queryset = RiskCategory.objects.all()