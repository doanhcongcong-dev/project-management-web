from django import forms
from .models import WazuhAlert

class AcknowledgeForm(forms.Form):
    # Không cần model form, chỉ cần nút xác nhận
    pass