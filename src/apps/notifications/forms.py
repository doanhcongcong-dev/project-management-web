from django import forms
from .models import Notification

class NotificationFilterForm(forms.Form):
    is_read = forms.ChoiceField(
        choices=[('', 'Tất cả'), ('False', 'Chưa đọc'), ('True', 'Đã đọc')],
        required=False,
        label='Trạng thái'
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