import os
import asyncio
from aiogram import Bot, Dispatcher, types
from fastapi import FastAPI, Request
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID"))
CHANNELS = ["@animesxda"]  # каналы для проверки подписки

bot = Bot(token=TOKEN)
dp = Dispatcher()
app = FastAPI()

# Простейшая база фильмов
FILMS = []

# Кнопки
def main_keyboard():
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton("📂 Архив фильмов", callback_data="show_films"),
        InlineKeyboardButton("✅ Проверка подписки", callback_data="check_sub"),
        InlineKeyboardButton("➕ Добавить фильм (только владелец)", callback_data="add_film")
    )
    return kb

# Проверка подписки
async def is_subscribed(user_id: int):
    for channel in CHANNELS:
        member = await bot.get_chat_member(chat_id=channel, user_id=user_id)
        if member.status in ["left", "kicked"]:
            return False
    return True

# Команда /start
@dp.message()
async def start(message: types.Message):
    await message.answer(
        f"Привет, {message.from_user.first_name}! Выбирай действие:",
        reply_markup=main_keyboard()
    )

# Обработка нажатий кнопок
@dp.callback_query()
async def callbacks(query: types.CallbackQuery):
    if query.data == "show_films":
        if not FILMS:
            await query.message.answer("Фильмы еще не добавлены.")
        else:
            await query.message.answer("\n".join(FILMS))

    elif query.data == "check_sub":
        subscribed = await is_subscribed(query.from_user.id)
        text = "Вы подписаны на все каналы ✅" if subscribed else "Вы не подписаны на все каналы ❌"
        await query.message.answer(text)

    elif query.data == "add_film":
        if query.from_user.id != OWNER_ID:
            await query.message.answer("Только владелец может добавлять фильмы.")
        else:
            await query.message.answer("Отправьте название фильма для добавления:")
            dp.current_state(chat=query.from_user.id, user=query.from_user.id).set_state("ADDING_FILM")

# Обработка добавления фильма владельцем
@dp.message(state="ADDING_FILM")
async def add_film(message: types.Message):
    FILMS.append(message.text)
    await message.answer(f"Фильм '{message.text}' добавлен!")
    await dp.current_state(chat=message.chat.id, user=message.from_user.id).clear_state()

# Webhook для Render
@app.post(f"/{TOKEN}")
async def telegram_webhook(req: Request):
    update = types.Update(**await req.json())
    await dp.feed_update(update)
    return {"ok": True}

# Запуск бота локально (long polling)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
