import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import FSInputFile
from mutagen.easyid3 import EasyID3

# Берём токен из Environment (добавь через Settings → Environment на Railway)
TOKEN = os.getenv("BOT_TOKEN")
if TOKEN is None:
    raise ValueError("BOT_TOKEN не найден! Добавь переменную через Settings → Environment.")

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Команда /start
@dp.message(commands=["start"])
async def start(msg: types.Message):
    await msg.answer(
        "Привет! Кидай MP3, я поменяю теги.\n"
        "Формат имени файла: Название — Исполнитель"
    )

# Обработка аудио
@dp.message(content_types=["audio"])
async def edit_tags(msg: types.Message):
    audio = msg.audio
    file = await bot.get_file(audio.file_id)

    os.makedirs("tmp", exist_ok=True)
    path = f"tmp/{audio.file_id}.mp3"
    await bot.download_file(file.file_path, path)

    # Парсим имя файла
    name = audio.file_name.replace(".mp3", "")
    if "—" in name:
        title, artist = name.split("—", 1)
        title = title.strip()
        artist = artist.strip()
    else:
        title = name
        artist = "Unknown"

    # Меняем теги
    tags = EasyID3(path)
    tags["title"] = title
    tags["artist"] = artist
    tags.save()

    # Отправляем обратно
    await msg.answer("Готово, держи👇")
    await msg.answer_audio(FSInputFile(path))


if __name__ == "__main__":
    import asyncio
    from aiogram import executor
    executor.start_polling(dp)
