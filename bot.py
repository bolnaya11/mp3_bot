import os
import io
from aiogram import Bot, Dispatcher, executor, types
from mutagen.id3 import ID3, APIC, TIT2, TPE1
from mutagen.mp3 import MP3
from PIL import Image

TOKEN = os.environ["8361301711:AAHpBB6liCtYgRnie1GDXkMY9COaLoYDDt8"]
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

user_data = {}

@dp.message_handler(content_types=['audio'])
async def get_mp3(msg: types.Message):
    file = await msg.audio.get_file()
    mp3_bytes = await bot.download_file(file.file_path)

    uid = msg.from_user.id
    user_data[uid] = {"mp3": mp3_bytes}
    await msg.answer("Окей, кидай новое название трека")

@dp.message_handler(lambda msg: msg.from_user.id in user_data and "title" not in user_data[msg.from_user.id])
async def set_title(msg: types.Message):
    uid = msg.from_user.id
    user_data[uid]["title"] = msg.text
    await msg.answer("Исполнитель?")

@dp.message_handler(lambda msg: msg.from_user.id in user_data and "artist" not in user_data[msg.from_user.id])
async def set_artist(msg: types.Message):
    uid = msg.from_user.id
    user_data[uid]["artist"] = msg.text
    await msg.answer("Теперь пришли картинку (обложку)")

@dp.message_handler(content_types=['photo'])
async def set_cover(msg: types.Message):
    uid = msg.from_user.id
    if uid not in user_data:
        return

    photo = msg.photo[-1]
    file = await photo.get_file()
    img_bytes = await bot.download_file(file.file_path)

    cover = Image.open(img_bytes)
    cover_buffer = io.BytesIO()
    cover.save(cover_buffer, format='jpeg')
    cover_bytes = cover_buffer.getvalue()

    mp3_bytes = user_data[uid]["mp3"]

    with open("track.mp3", "wb") as f:
        f.write(mp3_bytes.getvalue())

    audio = MP3("track.mp3", ID3=ID3)
    if audio.tags is None:
        audio.add_tags()

    audio.tags["TIT2"] = TIT2(encoding=3, text=user_data[uid]["title"])
    audio.tags["TPE1"] = TPE1(encoding=3, text=user_data[uid]["artist"])
    audio.tags["APIC"] = APIC(
        encoding=3,
        mime='image/jpeg',
        type=3,
        desc='Cover',
        data=cover_bytes
    )
    audio.save()

    await msg.answer_document(open("track.mp3", "rb"))

    os.remove("track.mp3")
    del user_data[uid]

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
