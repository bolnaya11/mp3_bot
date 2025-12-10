from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import os
from mutagen.id3 import ID3, APIC, TIT2, TPE1, TALB
from config import TELEGRAM_TOKEN, MP3_DIR, DEFAULT_ARTIST, DEFAULT_TITLE, DEFAULT_ALBUM, DEFAULT_COVER

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Пришли мне mp3, и я могу изменить её метаданные.")

async def edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Ждём файл и параметры
    await update.message.reply_text("Отправь mp3 с указанием названия, исполнителя и обложки (по желанию).")

# Для простоты пока обрабатываем только локально
def edit_mp3(file_path, title=None, artist=None, album=None, cover_path=None):
    if not os.path.exists(file_path):
        return "Файл не найден"

    title = title or DEFAULT_TITLE
    artist = artist or DEFAULT_ARTIST
    album = album or DEFAULT_ALBUM
    cover_path = cover_path or DEFAULT_COVER

    audio = ID3(file_path)
    audio["TIT2"] = TIT2(encoding=3, text=title)
    audio["TPE1"] = TPE1(encoding=3, text=artist)
    audio["TALB"] = TALB(encoding=3, text=album)

    if os.path.exists(cover_path):
        with open(cover_path, "rb") as albumart:
            audio["APIC"] = APIC(
                encoding=3,
                mime="image/jpeg",
                type=3,
                desc="Cover",
                data=albumart.read()
            )

    audio.save()
    return "Метаданные обновлены!"

if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("edit", edit))
    app.run_polling()
