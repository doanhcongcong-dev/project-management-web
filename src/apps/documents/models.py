import os
from django.db import models
from django.contrib.auth.models import User
from apps.projects.models import Project

def document_upload_path(instance, filename):
    """Đường dẫn lưu file: documents/project_<id>/<filename>"""
    return f'documents/project_{instance.project.id}/{filename}'

class Document(models.Model):
    DOCUMENT_TYPES = (
        ('spec', 'Đặc tả kỹ thuật'),
        ('design', 'Thiết kế'),
        ('test', 'Tài liệu test'),
        ('report', 'Báo cáo'),
        ('contract', 'Hợp đồng'),
        ('plan', 'Kế hoạch'),
        ('other', 'Khác'),
    )

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='documents',
        verbose_name='Dự án'
    )
    name = models.CharField(max_length=200, verbose_name='Tên tài liệu')
    file = models.FileField(
        upload_to=document_upload_path,
        verbose_name='File'
    )
    document_type = models.CharField(
        max_length=20,
        choices=DOCUMENT_TYPES,
        default='other',
        verbose_name='Loại tài liệu'
    )
    version = models.CharField(max_length=20, default='1.0', verbose_name='Phiên bản')
    description = models.TextField(blank=True, verbose_name='Mô tả')
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='uploaded_documents',
        verbose_name='Người tải lên'
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Tài liệu'
        verbose_name_plural = 'Tài liệu'
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.project.name} - {self.name} (v{self.version})"

    def get_file_size(self):
        """Trả về kích thước file dạng đọc được (KB, MB)"""
        if self.file and hasattr(self.file, 'size'):
            size = self.file.size
            if size < 1024:
                return f"{size} B"
            elif size < 1024 * 1024:
                return f"{size / 1024:.1f} KB"
            else:
                return f"{size / (1024 * 1024):.1f} MB"
        return "N/A"

    def get_file_extension(self):
        """Lấy phần mở rộng của file"""
        if self.file:
            name, ext = os.path.splitext(self.file.name)
            return ext.lower()
        return ''

    def get_file_icon(self):
        """Trả về icon Font Awesome dựa trên loại file"""
        ext = self.get_file_extension()
        icons = {
            '.pdf': 'fa-file-pdf',
            '.doc': 'fa-file-word',
            '.docx': 'fa-file-word',
            '.xls': 'fa-file-excel',
            '.xlsx': 'fa-file-excel',
            '.ppt': 'fa-file-powerpoint',
            '.pptx': 'fa-file-powerpoint',
            '.txt': 'fa-file-alt',
            '.zip': 'fa-file-archive',
            '.rar': 'fa-file-archive',
            '.jpg': 'fa-file-image',
            '.jpeg': 'fa-file-image',
            '.png': 'fa-file-image',
            '.gif': 'fa-file-image',
            '.mp4': 'fa-file-video',
            '.mp3': 'fa-file-audio',
        }
        return icons.get(ext, 'fa-file')