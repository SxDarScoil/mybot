# Используем официальный Python 3.12 образ
FROM python:3.12-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем все файлы проекта
COPY . /app

# Обновляем pip и устанавливаем зависимости
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Экспортируем переменные окружения, если нужно
# ENV OWNER_ID=8017932922
# ENV BOT_TOKEN=ваш_токен

# Запускаем бота
CMD ["python", "bot.py"]

