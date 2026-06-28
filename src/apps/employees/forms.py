from django import forms
from django.contrib.auth.models import User
from .models import EmployeeProfile

class EmployeeForm(forms.ModelForm):
    """Form cho EmployeeProfile (bao gồm cả User fields)"""
    username = forms.CharField(max_length=150, label='Tên đăng nhập')
    email = forms.EmailField(label='Email')
    first_name = forms.CharField(max_length=150, label='Họ và tên đệm')
    last_name = forms.CharField(max_length=150, label='Tên')
    password = forms.CharField(widget=forms.PasswordInput, required=False, label='Mật khẩu')

    class Meta:
        model = EmployeeProfile
        fields = [
            'employee_id', 'department', 'position', 'phone', 'address',
            'hire_date', 'birth_date', 'skills', 'avatar', 'is_active'
        ]
        widgets = {
            'hire_date': forms.DateInput(attrs={'type': 'date'}),
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'skills': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        self.instance_profile = kwargs.pop('instance_profile', None)
        super().__init__(*args, **kwargs)
        if self.instance_profile:
            user = self.instance_profile.user
            self.fields['username'].initial = user.username
            self.fields['email'].initial = user.email
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name

    def save(self, commit=True):
        profile = super().save(commit=False)
        user = profile.user if profile.pk else None

        # Xử lý User
        if not user:
            # Tạo user mới
            user = User.objects.create_user(
                username=self.cleaned_data['username'],
                email=self.cleaned_data['email'],
                password=self.cleaned_data['password']
            )
            profile.user = user
        else:
            # Cập nhật user
            user.username = self.cleaned_data['username']
            user.email = self.cleaned_data['email']
            user.first_name = self.cleaned_data['first_name']
            user.last_name = self.cleaned_data['last_name']
            if self.cleaned_data.get('password'):
                user.set_password(self.cleaned_data['password'])
            user.save()

        if commit:
            profile.save()
        return profile