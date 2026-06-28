from django import forms

class ReportFilterForm(forms.Form):
    start_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    project = forms.ChoiceField(required=False)
    status = forms.ChoiceField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from apps.projects.models import Project
        self.fields['project'].choices = [('', 'Tất cả')] + [(p.id, p.name) for p in Project.objects.all()]
        self.fields['status'].choices = [('', 'Tất cả')] + Task.STATUS_CHOICES