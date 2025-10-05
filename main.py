import os
import json
import asyncio
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import Command

load_dotenv()
API_TOKEN = os.getenv("BOT_TOKEN") 

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

current_page = {}


def load_json_data():
    with open("result.json", encoding="utf-8") as f:
        return json.load(f)


def build_categories_keyboard(categories, page=0, user_id=None):
    items_per_page = 9
    start_idx = page * items_per_page
    end_idx = start_idx + items_per_page
    page_categories = categories[start_idx:end_idx]
    
    inline_buttons = [
        [InlineKeyboardButton(text=cat.get("title", "Без имени"), url=cat.get("href", "#"))]
        for cat in page_categories
    ]
    
    nav_buttons = []
    if end_idx < len(categories):
        nav_buttons.append(InlineKeyboardButton(text="➡️ Далее", callback_data=f"next_page_{page + 1}"))
    
    if page > 0:
        nav_buttons.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"prev_page_{page - 1}"))
    
    if nav_buttons:
        inline_buttons.append(nav_buttons)
    
    inline_buttons.append([InlineKeyboardButton(text="🏠 Назад", callback_data="back_home")])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=inline_buttons)
    return keyboard

def build_marketplace_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🛍 Uzum", callback_data="market_uzum"),
            InlineKeyboardButton(text="🟨 Yandex", callback_data="market_yandex")
        ]
    ])
    return keyboard


@dp.message(Command("start"))
async def start_command(message: types.Message):
    await message.answer(
        "Привет! 👋\nВыберите маркетплейс, чтобы начать:",
        reply_markup=build_marketplace_keyboard()
    )


@dp.callback_query(lambda c: c.data.startswith("market_"))
async def select_market(callback: types.CallbackQuery):
    await callback.answer()
    if callback.data == "market_uzum":
        data = load_json_data()
        if not data:
            await callback.message.answer("Категории не найдены 😢")
            return
        user_id = callback.from_user.id
        current_page[user_id] = {"data": data, "page": 0}
        await callback.message.answer(
            "🛒 Категории Uzum:",
            reply_markup=build_categories_keyboard(data, 0, user_id)
        )
    elif callback.data == "market_yandex":
        await callback.message.answer(
            "Yandex Market пока находится в разработке 🛠️\nСкоро будет доступно! 🔜"
        )


@dp.message(Command("categories"))
async def show_json_categories(message: types.Message):
    data = load_json_data()
    if not data:
        await message.answer("Категории не найдены 😢")
        return
    
    user_id = message.from_user.id
    current_page[user_id] = {"data": data, "page": 0}
    
    await message.answer(
        "🛒 Все категории из JSON:",
        reply_markup=build_categories_keyboard(data, 0, user_id)
    )


@dp.callback_query(lambda c: c.data.startswith("next_page_") or c.data.startswith("prev_page_"))
async def handle_pagination(callback: types.CallbackQuery):
    await callback.answer()
    user_id = callback.from_user.id
    
    if user_id not in current_page:
        await callback.message.answer("Ошибка: данные не найдены. Попробуйте заново.")
        return
    
    if callback.data.startswith("next_page_"):
        new_page = int(callback.data.split("_")[2])
    else:  # prev_page_
        new_page = int(callback.data.split("_")[2])
    
    data = current_page[user_id]["data"]
    current_page[user_id]["page"] = new_page
    
    await callback.message.edit_reply_markup(
        reply_markup=build_categories_keyboard(data, new_page, user_id)
    )

@dp.callback_query(lambda c: c.data == "back_home")
async def callback_back_home(callback: types.CallbackQuery):
    await callback.answer()
    user_id = callback.from_user.id
    if user_id in current_page:
        del current_page[user_id]
    await start_command(callback.message)

if __name__ == "__main__":
    asyncio.run(dp.start_polling(bot))

