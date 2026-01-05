from aiogram import Router, F
from aiogram.types import Message, ContentType
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from config import ADMIN_USER_ID
from storage import load_products, save_products, add_product, update_product

router = Router()

class AdminStates(StatesGroup):
    waiting_for_action = State()
    waiting_for_product_id = State()
    waiting_for_name = State()
    waiting_for_quantity = State()
    waiting_for_price = State()
    waiting_for_description = State()
    waiting_for_city = State()
    waiting_for_photo = State()
    waiting_for_backup_choice = State()

async def is_admin(message: Message):
    return message.from_user.id == ADMIN_USER_ID

@router.message(F.text == "/admin")
async def admin_panel(message: Message, state: FSMContext):
    if not await is_admin(message):
        return
    await state.clear()
    await message.answer(
        "🛠 Админ-панель\n"
        "Выберите действие:\n"
        "/add — добавить товар\n"
        "/edit — редактировать товар\n"
        "/backup — получить резервную копию\n"
        "/restore — восстановить из файла"
    )

# === ADD PRODUCT ===
@router.message(F.text == "/add")
async def add_start(message: Message, state: FSMContext):
    if not await is_admin(message):
        return
    await state.set_state(AdminStates.waiting_for_name)
    await message.answer("Введите название товара:")

@router.message(AdminStates.waiting_for_name)
async def add_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(AdminStates.waiting_for_quantity)
    await message.answer("Введите количество (например, '5 г' или '10 мл'):")

@router.message(AdminStates.waiting_for_quantity)
async def add_quantity(message: Message, state: FSMContext):
    await state.update_data(quantity=message.text)
    await state.set_state(AdminStates.waiting_for_price)
    await message.answer("Введите цену (только число):")

@router.message(AdminStates.waiting_for_price)
async def add_price(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Введите корректное число:")
        return
    await state.update_data(price=int(message.text))
    await state.set_state(AdminStates.waiting_for_description)
    await message.answer("Введите описание:")

@router.message(AdminStates.waiting_for_description)
async def add_desc(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await state.set_state(AdminStates.waiting_for_city)
    await message.answer("Введите город (или '-' для пропуска):")

@router.message(AdminStates.waiting_for_city)
async def add_city(message: Message, state: FSMContext):
    city = None if message.text.strip() == "-" else message.text.strip()
    await state.update_data(city=city)
    await state.set_state(AdminStates.waiting_for_photo)
    await message.answer("Отправьте фото товара:")

@router.message(AdminStates.waiting_for_photo, F.content_type == ContentType.PHOTO)
async def add_photo(message: Message, state: FSMContext):
    photo_file_id = message.photo[-1].file_id
    data = await state.get_data()
    product = {
        "name": data["name"],
        "quantity": data["quantity"],
        "price": data["price"],
        "description": data["description"],
        "city": data.get("city"),
        "photo_file_id": photo_file_id,
        "available": True
    }
    await add_product(product)
    await state.clear()
    await message.answer("✅ Товар добавлен!")

# === EDIT / TOGGLE / BACKUP / RESTORE ===
# Для краткости — базовая реализация backup/restore:
@router.message(F.text == "/backup")
async def backup(message: Message):
    if not await is_admin(message):
        return
    await message.answer_document(document="products.json", caption="📁 Резервная копия")

@router.message(F.text == "/restore")
async def restore_start(message: Message, state: FSMContext):
    if not await is_admin(message):
        return
    await message.answer("Отправьте файл products.json для восстановления:")
    await state.set_state(AdminStates.waiting_for_backup_choice)

@router.message(AdminStates.waiting_for_backup_choice, F.content_type == ContentType.DOCUMENT)
async def restore_file(message: Message, state: FSMContext):
    if not message.document.file_name.endswith(".json"):
        await message.answer("Отправьте JSON-файл.")
        return
    file = await message.bot.get_file(message.document.file_id)
    await message.bot.download_file(file.file_path, "products.json")
    await state.clear()
    await message.answer("✅ Восстановлено!")
