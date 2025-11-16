# Используем официальный образ Python 3.12
FROM python:3.12-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы проекта
COPY . /app

# Устанавливаем зависимости
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Устанавливаем переменные окружения для Render (если нужно)
# ENV API_TOKEN=<твой_токен>
# ENV OWNER_ID=<твой_id>

# Expose порт, на котором будет работать FastAPI
EXPOSE 8000

# Запуск приложения
CMD ["python", "bot.py"]
