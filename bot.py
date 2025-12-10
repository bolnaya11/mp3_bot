import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, Filter
from aiogram.types import FSInputFile
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
from mutagen.id3 import APIC

TOKEN = "ВСТАВЬ_СЮДА_ТОКЕН"
SAVE_DIR = "audio_files"
os.makedirs(SAVE_DIR, exist_ok=True)

bot = Bot(token=TOKEN)
dp = Dispatcher()

# фильтр на аудио
class AudioFilter(Filter):
    async def __call__(self, message: types.Message) -> bool:
        return message.audio is not None

# временное хранилище состояния пользователя
user_state = {}

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer("Привет! Пришли мне MP3, и я сохраню с тегами и обложкой.")

@dp.message(AudioFilter())
async def audio_handler(message: types.Message):
    user_id = message.from_user.id
    audio = message.audio
    file_path = os.path.join(SAVE_DIR, audio.file_name)
    await audio.download(destination_file=file_path)

    # сохраняем путь и ждем данных от пользователя
    user_state[user_id] = {"file_path": file_path}
    await message.answer("Отлично! Теперь пришли название трека.")

@dp.message()
async def text_handler(message: types.Message):
    user_id = message.from_user.id
    if user_id in user_state:
        state = user_state[user_id]
        if "title" not in state:
            state["title"] = message.text
            await message.answer("Теперь укажи исполнителя.")
        elif "artist" not in state:
            state["artist"] = message.text
            await message.answer("Пришли обложку (картинку).")
        else:
            await message.answer("Жду обложку (картинку)!")
    else:
        await message.answer("Сначала пришли MP3!")

@dp.message(lambda message: message.photo)
async def photo_handler(message: types.Message):
    user_id = message.from_user.id
    if user_id not in user_state or "artist" not in user_state[user_id]:
        await message.answer("Сначала нужно указать название и исполнителя.")
        return

    state = user_state[user_id]
    photo = message.photo[-1]
    photo_path = os.path.join(SAVE_DIR, f"{state['title']}_cover.jpg")
    await photo.download(destination_file=photo_path)

    # применяем теги к MP3
    try:
        mp3_file = MP3(state["file_path"], ID3=EasyID3)
        mp3_file["title"] = state["title"]
        mp3_file["artist"] = state["artist"]
        mp3_file.save()

        # добавляем обложку
        mp3_file = MP3(state["file_path"])
        mp3_file.tags.add(
            APIC(
                encoding=3,  # UTF-8
                mime='image/jpeg',
                type=3,  # обложка
                desc='Cover',
                data=open(photo_path, 'rb').read()
            )
        )
        mp3_file.save()
        await message.answer(f"Аудио {state['title']} сохранено с тегами и обложкой!")
        user_state.pop(user_id)
    except Exception as e:
        await message.answer(f"Произошла ошибка при сохранении тегов: {e}")

async def main():
    print("Бот запущен")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
