import os
import json
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.enums.chat_member_status import ChatMemberStatus

from fastapi import FastAPI, Request
import asyncio

API_TOKEN = os.getenv("API_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))
PORT = int(os.getenv("PORT", 8000))
APP_URL = os.getenv("RENDER_EXTERNAL_URL")  # Render внешняя ссылка

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
app = FastAPI()

# --- Функции проверки подписки ---
async def check_subscription(user_id: int, channel_username: str, bot):
    try:
        member = await bot.get_chat_member(chat_id=channel_username, user_id=user_id)
        return member.status in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
    except:
        return False

# --- Главное меню с кнопками ---
def main_menu(user_id: int):
    buttons = [
        [InlineKeyboardButton(text="Проверить подписку", callback_data="check_sub")],
        [InlineKeyboardButton(text="Архив фильмов", callback_data="movie_archive")],
        [InlineKeyboardButton(text="Получить фильм", callback_data="get_film")]
    ]
    if user_id == OWNER_ID:
        buttons.append([InlineKeyboardButton(text="Добавить фильм", callback_data="add_film")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# --- Обработчики кнопок ---
@dp.callback_query(F.data == "check_sub")
async def callback_check_sub(callback: CallbackQuery):
    user_id = callback.from_user.id
    if await check_subscription(user_id, "@my_channel", callback.bot):
        await callback.message.answer("Вы подписаны на канал ✅")
    else:
        await callback.message.answer("Вы не подписаны на канал ❌")

@dp.callback_query(F.data == "movie_archive")
async def callback_movie_archive(callback: CallbackQuery):
    if os.path.exists("movies.json"):
        with open("movies.json", "r", encoding="utf-8") as f:
            movies = json.load(f)
    else:
        movies = []
    if movies:
        text = "\n".join(movies)
    else:
        text = "Архив фильмов пуст."
    await callback.message.answer(text)

@dp.callback_query(F.data == "get_film")
async def callback_get_film(callback: CallbackQuery):
    user_id = callback.from_user.id
    if await check_subscription(user_id, "@my_channel", callback.bot):
        if os.path.exists("movies.json"):
            with open("movies.json", "r", encoding="utf-8") as f:
                movies = json.load(f)
        else:
            movies = []
        if movies:
            await callback.message.answer(f"Название фильма: {movies[0]} 🎬")
        else:
            await callback.message.answer("Фильмов пока нет.")
    else:
        await callback.message.answer("Чтобы получить фильм, подпишитесь на канал!")

# --- Добавление фильма владельцем через кнопку ---
@dp.callback_query(F.data == "add_film")
async def callback_add_film(callback: CallbackQuery):
    user_id = callback.from_user.id
    if user_id != OWNER_ID:
        await callback.message.answer("Эта кнопка доступна только владельцу.")
        return
    await callback.message.answer("Введите название фильма, чтобы добавить его в архив:")

    # Ждём ответ владельца с названием фильма
    def check(m: Message):
        return m.from_user.id == OWNER_ID

    try:
        response = await dp.wait_for_message(check, timeout=120)  # 2 минуты на ввод
        film_name = response.text.strip()

        if os.path.exists("movies.json"):
            with open("movies.json", "r", encoding="utf-8") as f:
                movies = json.load(f)
        else:
            movies = []

        movies.append(film_name)

        with open("movies.json", "w", encoding="utf-8") as f:
            json.dump(movies, f, ensure_ascii=False, indent=4)

        await response.answer(f"Фильм '{film_name}' добавлен в архив ✅")
    except asyncio.TimeoutError:
        await callback.message.answer("Время ввода истекло. Попробуйте снова.")

# --- /start ---
@dp.message(F.text == "/start")
async def start(message: Message):
    await message.answer("Привет! Выберите действие:", reply_markup=main_menu(message.from_user.id))

# --- Webhook для Render ---
WEBHOOK_PATH = f"/{API_TOKEN}"
WEBHOOK_URL = f"{APP_URL}{WEBHOOK_PATH}"

@app.on_event("startup")
async def on_startup():
    await bot.set_webhook(WEBHOOK_URL)

@app.on_event("shutdown")
async def on_shutdown():
    await bot.delete_webhook()

@app.post(WEBHOOK_PATH)
async def telegram_webhook(request: Request):
    update = await request.json()
    await dp.feed_update(update)
    return {"ok": True}

# --- Запуск локально ---
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)
