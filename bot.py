import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, Filter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3

TOKEN = "8361301711:AAHpBB6liCtYgRnie1GDXkMY9COaLoYDDt8"
SAVE_DIR = "audio_files"
COVER_DIR = "covers"

os.makedirs(SAVE_DIR, exist_ok=True)
os.makedirs(COVER_DIR, exist_ok=True)

bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# FSM состояния
class AudioForm(StatesGroup):
    waiting_for_track_name = State()
    waiting_for_artist_name = State()
    waiting_for_cover = State()

# фильтр на аудио
class AudioFilter(Filter):
    async def __call__(self, message: types.Message) -> bool:
        return message.audio is not None

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer("Привет! Пришли мне MP3, и я сохраню её с тегами.")

@dp.message(AudioFilter())
async def audio_handler(message: types.Message, state: FSMContext):
    # сохраняем временно имя файла в FSM
    await state.update_data(file_name=message.audio.file_name)
    await state.update_data(file_id=message.audio.file_id)
    await message.answer("Как называется этот трек?")
    await state.set_state(AudioForm.waiting_for_track_name)

@dp.message(AudioForm.waiting_for_track_name)
async def track_name_handler(message: types.Message, state: FSMContext):
    await state.update_data(track_name=message.text)
    await message.answer("Кто исполнитель?")
    await state.set_state(AudioForm.waiting_for_artist_name)

@dp.message(AudioForm.waiting_for_artist_name)
async def artist_name_handler(message: types.Message, state: FSMContext):
    await state.update_data(artist_name=message.text)
    await message.answer("Пришли обложку (картинку) для трека или напиши 'нет', чтобы пропустить")
    await state.set_state(AudioForm.waiting_for_cover)

@dp.message(AudioForm.waiting_for_cover, content_types=types.ContentType.ANY)
async def cover_handler(message: types.Message, state: FSMContext):
    data = await state.get_data()
    file_name = data["file_name"]
    file_id = data["file_id"]
    track_name = data["track_name"]
    artist_name = data["artist_name"]

    file_path = os.path.join(SAVE_DIR, file_name)

    # скачиваем MP3
    file = await bot.get_file(file_id)
    await file.download(destination_file=file_path)

    # если пришла картинка — сохраняем её
    if message.photo:
        cover_file = message.photo[-1]  # берём фото с наибольшим разрешением
        cover_path = os.path.join(COVER_DIR, f"{track_name}_cover.jpg")
        await cover_file.download(destination_file=cover_path)
    elif message.text.lower() == "нет":
        cover_path = None
    else:
        cover_path = None

    # записываем теги
    try:
        mp3_file = MP3(file_path, ID3=EasyID3)
        mp3_file["title"] = track_name
        mp3_file["artist"] = artist_name
        mp3_file.save()
        await message.answer(f"Аудио '{track_name}' сохранено с тегами!")
    except Exception as e:
        await message.answer(f"Аудио сохранено, но не удалось прописать теги: {e}")

    await state.clear()  # сброс состояния

async def main():
    print("Бот запущен")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
