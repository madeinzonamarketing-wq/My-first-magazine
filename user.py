from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from storage import load_products

router = Router()

@router.message(F.text == "/start")
async def send_catalog(message: Message):
    products = await load_products()
    available = [p for p in products if p.get("available", True)]
    if not available:
        await message.answer("Каталог временно пуст.")
        return
    for p in available:
        caption = f"<b>{p['name']}</b>\n"
        if p.get("quantity"):
            caption += f"Объём: {p['quantity']}\n"
        if p.get("city"):
            caption += f"Город: {p['city']}\n"
        caption += f"Цена: {p['price']} ₽\n\n{p.get('description', '')}"
        await message.answer_photo(photo=p["photo_file_id"], caption=caption, parse_mode="HTML")
