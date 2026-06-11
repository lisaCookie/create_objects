FROM python:3.12-slim

# Устанавливаем системные зависимости, чтобы база данных смогла подключиться
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем зависимости
COPY pyproject.toml .

# Устанавливаем зависимости
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir .

RUN pip install flask flask_wtf wtforms gunicorn

# Копируем ВСЕ файлы проекта (включая новый entrypoint.sh)
COPY . .

# Даем файлу entrypoint.sh право на запуск
RUN chmod +x entrypoint.sh

# Запускаем наш пусковой файл
ENTRYPOINT ["./entrypoint.sh"]