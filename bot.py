import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, Filter

TOKEN = "ВСТАВЬ_СЮДА_ТОКЕН"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# фильтр на аудио
class AudioFilter(Filter):
    async def __call__(self, message: types.Message) -> bool:
        return message.audio is not None

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer("Привет! Пришли мне MP3.")

@dp.message(AudioFilter())
async def audio_handler(message: types.Message):
    audio = message.audio
    await message.answer(f"Принял аудио: {audio.file_name}")

async def main():
    print("Бот запущен")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())


