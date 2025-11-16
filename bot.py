import asyncio
import json
from pathlib import Path
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

import os

API_TOKEN = os.getenv("8052669939:AAEz5BodFrf9Nk5wWEFRz7-8lF4N4koYRgg")
OWNER_ID = int(os.getenv("8017932922"))

FILE_PATH = Path("movies.json")
REQUIRED_CHANNELS = ["animesxda"]  # список каналов для подписки

# -------------------------
# Загрузка кодов фильмов
if FILE_PATH.exists():
    with FILE_PATH.open("r", encoding="utf-8") as f:
        movie_codes = json.load(f)
else:
    movie_codes = {}

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

def save_movies():
    with FILE_PATH.open("w", encoding="utf-8") as f:
        json.dump(movie_codes, f, ensure_ascii=False, indent=4)

# -------------------------
async def check_subscription(user_id: int) -> bool:
    """Проверка подписки пользователя на все REQUIRED_CHANNELS"""
    for channel in REQUIRED_CHANNELS:
        try:
            member = await bot.get_chat_member(chat_id=f"@{channel}", user_id=user_id)
            if member.status in ["left", "kicked"]:
                return False
        except Exception as e:
            print(f"Ошибка проверки подписки @{channel}: {e}")
            return False
    return True

# -------------------------
def subscription_keyboard():
    """Кнопка для подписки на канал и проверки"""
    buttons = [InlineKeyboardButton(text=f"Подписаться на @{c}", url=f"https://t.me/{c}") for c in REQUIRED_CHANNELS]
    buttons.append(InlineKeyboardButton(text="Я подписался ✅", callback_data="check_sub"))
    return InlineKeyboardMarkup(inline_keyboard=[[b] for b in buttons])

def archive_keyboard():
    """Кнопка Архив всех фильмов"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Архив всех фильмов 📚", callback_data="show_archive")]
    ])

# -------------------------
@dp.message(Command("start"))
async def start_command(message: types.Message):
    if not await check_subscription(message.from_user.id):
        await message.answer(
            "⚠ Чтобы получать фильмы, подпишитесь на канал(ы) ниже и нажмите 'Я подписался' после подписки:",
            reply_markup=subscription_keyboard()
        )
    else:
        await message.answer(
            "Вы подписаны на все каналы ✅",
            reply_markup=archive_keyboard()
        )

# -------------------------
@dp.callback_query()
async def handle_callback_query(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    data = callback_query.data

    if data == "check_sub":
        if await check_subscription(user_id):
            await callback_query.message.edit_text(
                "Вы подписаны на все каналы ✅",
                reply_markup=archive_keyboard()
            )
        else:
            await callback_query.answer("Вы ещё не подписаны на все каналы.", show_alert=True)

    elif data == "show_archive":
        if movie_codes:
            movies_text = "\n".join([f"{code} — {name}" for code, name in movie_codes.items()])
        else:
            movies_text = "Архив пуст."
        await callback_query.message.answer(f"🎬 Архив фильмов:\n{movies_text}")

# -------------------------
@dp.message()
async def handle_message(message: types.Message):
    user_id = message.from_user.id
    text = message.text.strip()

    if user_id == OWNER_ID:
        # Владелец управляет кодами
        if "|" in text and not text.lower().startswith("del"):
            code, movie = map(str.strip, text.split("|", 1))
            movie_codes[code] = movie
            save_movies()
            await message.answer(f"✅ Код '{code}' добавлен для фильма '{movie}'")
        elif text.lower().startswith("del|"):
            _, code = map(str.strip, text.split("|", 1))
            if code in movie_codes:
                removed = movie_codes.pop(code)
                save_movies()
                await message.answer(f"❌ Код '{code}' удалён, фильм '{removed}'")
            else:
                await message.answer(f"❌ Код '{code}' не найден")
        else:
            await message.answer("ℹ Используйте формат: код|название или del|код")
    else:
        # Пользователь получает фильм по коду
        if text in movie_codes:
            await message.answer(f"🎬 Название фильма: {movie_codes[text]}")
        else:
            await message.answer("❌ Неверный код или фильм не найден.")

# -------------------------
async def main():
    await bot.delete_webhook()
    print("Бот запущен и готов к работе!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
