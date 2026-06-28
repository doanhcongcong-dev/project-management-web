FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Cài các gói hệ thống cần thiết
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ .

# Chạy migrations và collectstatic khi start (có thể dùng entrypoint)
# Nhưng tạm thời để runserver, bạn có thể chạy riêng
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]