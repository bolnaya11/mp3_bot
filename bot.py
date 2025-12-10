import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.utils.keyboard import ReplyKeyboardMarkup, KeyboardButton
from mutagen.easyid3 import EasyID3

load_dotenv()

TOKEN = os.getenv("8361301711:AAHpBB6liCtYgRnie1GDXkMY9COaLoYDDt8")
bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(commands=["start"])
async def start(msg: types.Message):
    await msg.answer("Кидай MP3, я поменяю теги. Формат:\n\nНазвание — Автор")


@dp.message(content_types=["audio"])
async def edit_tags(msg: types.Message):
    audio = msg.audio
    file = await bot.get_file(audio.file_id)

    path = f"tmp/{audio.file_id}.mp3"
    os.makedirs("tmp", exist_ok=True)

    await bot.download_file(file.file_path, path)

    # Попытка парсить название файла
    # ожидаем формат "Название — Автор"
    name = audio.file_name.replace(".mp3", "")
    
    if "—" in name:
        title, artist = name.split("—", 1)
        title = title.strip()
        artist = artist.strip()
    else:
        title = name
        artist = "Unknown"

    tags = EasyID3(path)
    tags["title"] = title
    tags["artist"] = artist
    tags.save()

    await msg.answer("Готово, держи👇")
    
    await msg.answer_audio(types.FSInputFile(path))


if __name__ == "__main__":
    import asyncio
    from aiogram import executor

    executor.start_polling(dp)
