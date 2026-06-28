from django import forms

class OTPVerificationForm(forms.Form):
    otp_code = forms.CharField(
        label='Mã OTP',
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nhập 6 số'})
    )

class Enable2FAForm(forms.Form):
    confirm = forms.BooleanField(
        label='Tôi xác nhận bật xác thực 2 yếu tố',
        required=True
    )