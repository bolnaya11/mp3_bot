import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InputFile
from mutagen.easyid3 import EasyID3
import io

TOKEN = "8361301711:AAHpBB6liCtYgRnie1GDXkMY9COaLoYDDt8"

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer("Кидай MP3, я поменяю теги. Формат имени файла: Название — Исполнитель")

@dp.message(content_types=types.ContentType.AUDIO)
async def audio_handler(message: types.Message):
    audio = message.audio
    file = await bot.get_file(audio.file_id)

    mp3_bytes = await bot.download_file(file.file_path)
    data = io.BytesIO(mp3_bytes.read())

    name = audio.file_name.replace(".mp3", "")
    if "—" in name:
        title, artist = name.split("—", 1)
        title = title.strip()
        artist = artist.strip()
    else:
        title = name
        artist = "Unknown"

    tags = EasyID3(data)
    tags["title"] = title
    tags["artist"] = artist
    tags.save()

    data.seek(0)
    await message.answer_audio(InputFile(data, filename=audio.file_name))

async def main():
    print("Бот запущен")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

