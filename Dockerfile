# Dockerfile
FROM python:3.11-slim

# Установка рабочей директории
WORKDIR /app

# Копирование requirements.txt и установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование всех остальных файлов проекта
COPY . .

# Команда для запуска вашего бота
CMD ["python", "main.py"]