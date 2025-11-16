#!/bin/bash
# start.sh — безопасный запуск Telegram бота с логированием

# Проверка обязательных переменных окружения
if [ -z "$API_TOKEN" ]; then
  echo "Ошибка: переменная API_TOKEN не установлена!"
  exit 1
fi

if [ -z "$OWNER_ID" ]; then
  echo "Ошибка: переменная OWNER_ID не установлена!"
  exit 1
fi

echo "Запуск бота..."
echo "Время запуска: $(date)"
echo "API_TOKEN: ${API_TOKEN:0:5}***"  # показываем только начало токена
echo "OWNER_ID: $OWNER_ID"

# Активируем виртуальное окружение, если есть
if [ -f ".venv/bin/activate" ]; then
    echo "Активируем виртуальное окружение"
    source .venv/bin/activate
fi

# Запуск бота с логами
python bot.py 2>&1 | tee bot.log
