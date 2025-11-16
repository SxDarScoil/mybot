import os
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from fastapi import FastAPI, Request
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# ======================
# Переменные окружения
# ======================
TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID"))
CHANNELS = list(map(int, os.getenv("CHANNELS").split(",")))  # Список ID каналов

bot = Bot(token=TOKEN)
dp = Dispatcher()
app = FastAPI()

# Хранилище фильмов
FILMS = []

# Состояние FSM для добавления фильма
class AddFilmState(StatesGroup):
    waiting_for_film = State()

# ======================
# Кнопки
# ======================
def main_keyboard():
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📂 Архив фильмов", callback_data="show_films")],
        [InlineKeyboardButton(text="✅ Проверка подписки", callback_data="check_sub")],
        [InlineKeyboardButton(text="➕ Добавить фильм (только владелец)", callback_data="add_film")],
    ])
    return kb

# ======================
# Проверка подписки
# ======================
async def is_subscribed(user_id: int) -> bool:
    for channel_id in CHANNELS:
        try:
            member = await bot.get_chat_member(channel_id, user_id)
            if member.status in ["left", "kicked"]:
                return False
        except Exception:
            return False
    return True

# ======================
# Команда /start
# ======================
@dp.message(F.text == "/start")
async def start(message: types.Message):
    await message.answer(
        f"Привет, {message.from_user.first_name}! 👋\nВыбирай действие:",
        reply_markup=main_keyboard()
    )

# ======================
# Обработка кнопок
# ======================
@dp.callback_query(F.data == "show_films")
async def show_films(query: types.CallbackQuery):
    if not FILMS:
        await query.message.answer("📭 Фильмы ещё не добавлены.")
    else:
        text = "📚 *Архив фильмов:*\n\n" + "\n".join([f"• {f}" for f in FILMS])
        await query.message.answer(text, parse_mode="Markdown")

    await query.answer()

@dp.callback_query(F.data == "check_sub")
async def check_subscription(query: types.CallbackQuery):
    subscribed = await is_subscribed(query.from_user.id)
    text = "✅ Вы подписаны на все каналы!" if subscribed else "❌ Вы не подписаны на один или несколько каналов!"
    await query.message.answer(text)
    await query.answer()

@dp.callback_query(F.data == "add_film")
async def add_film_button(query: types.CallbackQuery, state: FSMContext):
    if query.from_user.id != OWNER_ID:
        await query.message.answer("⛔ Только владелец может добавлять фильмы.")
    else:
        await query.message.answer("Введите название фильма:")
        await state.set_state(AddFilmState.waiting_for_film)

    await query.answer()

# ======================
# Добавление фильма
# ======================
@dp.message(AddFilmState.waiting_for_film)
async def process_film(message: types.Message, state: FSMContext):
    FILMS.append(message.text)
    await message.answer(f"✅ Фильм *{message.text}* добавлен!", parse_mode="Markdown")
    await state.clear()

# ======================
# Webhook для Render
# ======================
@app.post(f"/{TOKEN}")
async def webhook(request: Request):
    data = await request.json()
    update = types.Update(**data)
    await dp.feed_update(bot, update)
    return {"ok": True}

# ======================
# Локальный запуск (для тестов)
# ======================
if __name__ == "__main__":
    import uvicorn
    print("Бот запущен локально!")
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
