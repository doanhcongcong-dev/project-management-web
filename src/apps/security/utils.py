import base64
from cryptography.fernet import Fernet
from django.conf import settings

# Lưu ý: bạn cần đặt FERNET_KEY trong settings.py hoặc .env
# Nếu chưa có, tự tạo và lưu vào settings
def get_fernet_key():
    key = getattr(settings, 'FERNET_KEY', None)
    if not key:
        # Tạo key mới (chỉ dùng khi phát triển, trong production nên cố định)
        key = Fernet.generate_key()
        # Ghi chú: bạn nên lưu key vào biến môi trường hoặc file cấu hình
        setattr(settings, 'FERNET_KEY', key)
    return key

def encrypt_data(data):
    """Mã hóa dữ liệu (chuỗi)"""
    if not data:
        return data
    try:
        fernet = Fernet(get_fernet_key())
        encrypted = fernet.encrypt(data.encode('utf-8'))
        return base64.urlsafe_b64encode(encrypted).decode('utf-8')
    except Exception:
        return data

def decrypt_data(encrypted_data):
    """Giải mã dữ liệu"""
    if not encrypted_data:
        return encrypted_data
    try:
        fernet = Fernet(get_fernet_key())
        decoded = base64.urlsafe_b64decode(encrypted_data.encode('utf-8'))
        decrypted = fernet.decrypt(decoded)
        return decrypted.decode('utf-8')
    except Exception:
        return encrypted_data