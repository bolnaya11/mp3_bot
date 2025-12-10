import os
from mutagen.id3 import ID3, APIC, TIT2, TPE1, TALB
from telegram import Update, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters, ConversationHandler
from config import TELEGRAM_TOKEN, DEFAULT_TITLE, DEFAULT_ARTIST, DEFAULT_ALBUM

# Состояния для ConversationHandler
ASK_TITLE, ASK_ARTIST, ASK_COVER = range(3)

# Временное хранение данных
user_data_dict = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Пришли мне MP3, и я могу изменить её метаданные.")

async def receive_mp3(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = update.message.audio
    if not file:
        await update.message.reply_text("Пожалуйста, отправь именно MP3-файл.")
        return ConversationHandler.END

    file_path = f"./temp_{update.message.from_user.id}.mp3"
    await file.download_to_drive(file_path)
    user_data_dict[update.message.from_user.id] = {"file_path": file_path}

    await update.message.reply_text("Отлично! Какое название поставить?")
    return ASK_TITLE

async def ask_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_data_dict[user_id]["title"] = update.message.text or DEFAULT_TITLE
    await update.message.reply_text("Кто исполнитель?")
    return ASK_ARTIST

async def ask_artist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_data_dict[user_id]["artist"] = update.message.text or DEFAULT_ARTIST
    await update.message.reply_text("Отправь обложку (картинку) или напиши 'нет', чтобы оставить без обложки.")
    return ASK_COVER

async def ask_cover(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    cover_path = None

    if update.message.photo:
        photo_file = await update.message.photo[-1].get_file()
        cover_path = f"./cover_{user_id}.jpg"
        await photo_file.download_to_drive(cover_path)
    elif update.message.text.lower() != "нет":
        await update.message.reply_text("Не понял, нужно отправить картинку или написать 'нет'.")
        return ASK_COVER

    data = user_data_dict[user_id]
    file_path = data["file_path"]
    title = data["title"]
    artist = data["artist"]

    # Изменяем MP3
    audio = ID3(file_path)
    audio["TIT2"] = TIT2(encoding=3, text=title)
    audio["TPE1"] = TPE1(encoding=3, text=artist)
    audio["TALB"] = TALB(encoding=3, text=DEFAULT_ALBUM)
    if cover_path and os.path.exists(cover_path):
        with open(cover_path, "rb") as albumart:
            audio["APIC"] = APIC(
                encoding=3,
                mime="image/jpeg",
                type=3,
                desc="Cover",
                data=albumart.read()
            )
    audio.save()

    # Отправляем готовый MP3
    await update.message.reply_audio(audio=InputFile(file_path))

    # Чистим временные файлы
    os.remove(file_path)
    if cover_path and os.path.exists(cover_path):
        os.remove(cover_path)
    del user_data_dict[user_id]

    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Отмена операции.")
    return ConversationHandler.END

if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.AUDIO, receive_mp3)],
        states={
            ASK_TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_title)],
            ASK_ARTIST: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_artist)],
            ASK_COVER: [MessageHandler(filters.PHOTO | (filters.TEXT & ~filters.COMMAND), ask_cover)],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv_handler)
    app.run_polling()

