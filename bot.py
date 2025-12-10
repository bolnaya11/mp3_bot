from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram import F
from aiogram import Router

TOKEN = "твой_токен"

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# FSM состояния
class TrackInfo(StatesGroup):
    name = State()
    artist = State()
    cover = State()

router = Router()

@router.message(Command("start"))
async def start(message: types.Message, state: FSMContext):
    await message.answer("Привет! Введи название трека:")
    await state.set_state(TrackInfo.name)

@router.message(F.text, TrackInfo.name)
async def get_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Теперь введи исполнителя:")
    await state.set_state(TrackInfo.artist)

@router.message(F.text, TrackInfo.artist)
async def get_artist(message: types.Message, state: FSMContext):
    await state.update_data(artist=message.text)
    await message.answer("Теперь отправь обложку (фото):")
    await state.set_state(TrackInfo.cover)

@router.message(F.photo, TrackInfo.cover)
async def get_cover(message: types.Message, state: FSMContext):
    data = await state.get_data()
    name = data['name']
    artist = data['artist']
    photo = message.photo[-1].file_id
    await message.answer(f"Готово!\nНазвание: {name}\nИсполнитель: {artist}\nОбложка получена.")
    await state.clear()

dp.include_router(router)
