from django import forms
from .models import ActivityLog
from django.contrib.auth.models import User

class ActivityLogFilterForm(forms.Form):
    user = forms.ModelChoiceField(
        queryset=User.objects.filter(is_active=True),
        required=False,
        label='Người dùng'
    )
    action = forms.ChoiceField(
        choices=[('', 'Tất cả')] + list(ActivityLog.ACTION_CHOICES),
        required=False,
        label='Hành động'
    )
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
        label='Từ ngày'
    )
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
        label='Đến ngày'
    )
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Tìm kiếm mô tả...'}),
        label='Tìm kiếm'
    )