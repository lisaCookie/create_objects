FROM python:3.12-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем зависимости
COPY pyproject.toml .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir .

RUN pip install flask flask_wtf wtforms

# Копируем исходники
COPY . .

# Запускаем приложение
CMD ["python", "app.py"]