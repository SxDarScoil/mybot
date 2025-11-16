# Используем Python 3.12 slim
FROM python:3.12-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы
COPY . /app

# Обновляем pip и устанавливаем зависимости
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Экспортируем порт
EXPOSE 8000

# Команда запуска (uvicorn для FastAPI + Aiogram)
CMD ["uvicorn", "bot:app", "--host", "0.0.0.0", "--port", "8000"]

