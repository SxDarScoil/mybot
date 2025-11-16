# Используем официальный образ Python 3.11
FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем все файлы проекта
COPY . .

# Обновляем pip и устанавливаем зависимости
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Делаем скрипт запуска исполняемым
RUN chmod +x start.sh

# Устанавливаем переменные окружения (при необходимости)
# ENV OWNER_ID=ваш_owner_id
# ENV BOT_TOKEN=ваш_токен

# Команда запуска
CMD ["./start.sh"]
