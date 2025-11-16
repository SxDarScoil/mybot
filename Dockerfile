FROM python:3.12-slim

WORKDIR /app
COPY bot.py .

RUN pip install --no-cache-dir aiogram==3.2.0 fastapi uvicorn

EXPOSE 8000

CMD ["python", "bot.py"]
