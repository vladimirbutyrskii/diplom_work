# Базовый образ Python
FROM python:3.12-slim

# Предотвращение создания .pyc файлов и буферизации вывода
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Рабочая директория внутри контейнера
WORKDIR /app

# Установка системных зависимостей для psycopg2 и Pillow
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    libjpeg-dev \
    zlib1g-dev curl && \
    rm -rf /var/lib/apt/lists/*

# Копирование и установка Python-зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование всего проекта
COPY . .

# Создание директорий для статики и медиа
RUN mkdir -p /app/staticfiles /app/media

# Сбор статики
RUN python manage.py collectstatic --noinput || echo "Static collection skipped"

# Пользователь без root-прав (безопасность)
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Порт приложения
EXPOSE 8000

# Команда запуска
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
