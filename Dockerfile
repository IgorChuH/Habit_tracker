# Используем официальный образ Python
FROM python:3.13-slim

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем requirements.txt
COPY requirements.txt .

# Устанавливаем зависимости Python
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект
COPY . .

# Делаем скрипт entrypoint исполняемым
RUN chmod +x docker/scripts/entrypoint.sh

# Указываем порт
EXPOSE 8000

# Точка входа
ENTRYPOINT ["/app/docker/scripts/entrypoint.sh"]