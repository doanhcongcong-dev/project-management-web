from django import forms
from .models import Document

class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['project', 'name', 'file', 'document_type', 'version', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'version': forms.TextInput(attrs={'placeholder': '1.0'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        # Chỉ hiển thị các dự án mà user tham gia
        if user and not user.is_staff:
            self.fields['project'].queryset = user.projects.all()
        # Nếu là edit, không cho phép upload file mới (có thể để trống)
        if self.instance and self.instance.pk:
            self.fields['file'].required = False
            self.fields['file'].help_text = 'Để trống nếu không muốn thay đổi file'

    def clean_file(self):
        """Validate file: kiểm tra kích thước và loại"""
        file = self.cleaned_data.get('file')
        if file:
            # Giới hạn kích thước 20MB
            if file.size > 20 * 1024 * 1024:
                raise forms.ValidationError('File không được lớn hơn 20MB.')
            # Kiểm tra phần mở rộng
            ext = file.name.split('.')[-1].lower()
            allowed_extensions = ['pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt', 'zip', 'rar', 'jpg', 'jpeg', 'png', 'gif', 'mp4', 'mp3']
            if ext not in allowed_extensions:
                raise forms.ValidationError('Định dạng file không được hỗ trợ.')
        return file