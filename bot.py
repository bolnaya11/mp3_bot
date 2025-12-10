from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram import Router
import logging

TOKEN = "8361301711:AAHpBB6liCtYgRnie1GDXkMY9COaLoYDDt8"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())
router = Router()

# FSM состояния
class TrackInfo(StatesGroup):
    name = State()
    artist = State()
    cover = State()

# Команда /start
@router.message(Command("start"))
async def start(message: types.Message, state: FSMContext):
    await message.answer("Привет! Введи название трека:")
    await state.set_state(TrackInfo.name)

# Получение названия
@router.message(TrackInfo.name)
async def get_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Теперь введи исполнителя:")
    await state.set_state(TrackInfo.artist)

# Получение исполнителя
@router.message(TrackInfo.artist)
async def get_artist(message: types.Message, state: FSMContext):
    await state.update_data(artist=message.text)
    await message.answer("Теперь отправь обложку (фото):")
    await state.set_state(TrackInfo.cover)

# Получение обложки
@router.message(TrackInfo.cover)
async def get_cover(message: types.Message, state: FSMContext):
    if not message.photo:
        await message.answer("Это не фото, отправь, пожалуйста, обложку.")
        return
    data = await state.get_data()
    name = data['name']
    artist = data['artist']
    photo = message.photo[-1].file_id
    await message.answer(f"Готово!\nНазвание: {name}\nИсполнитель: {artist}\nОбложка получена.")
    await state.clear()

dp.include_router(router)

if __name__ == "__main__":
    from aiogram import asyncio
    asyncio.run(dp.start_polling(bot))
