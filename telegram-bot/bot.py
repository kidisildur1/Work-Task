import os
import requests
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:8000/api/tasks/from-telegram')

bot = Bot(BOT_TOKEN)
dp = Dispatcher()


@dp.message(CommandStart())
async def start_handler(message: Message):
    await message.answer('Отправьте текст или голос — я создам задачу в системе лаборатории.')


@dp.message(F.voice)
async def voice_handler(message: Message):
    payload = {
        'telegram_user_id': str(message.from_user.id),
        'username': message.from_user.username,
        'message_type': 'voice',
        'voice_file_id': message.voice.file_id,
        'audio_file_id': message.voice.file_id,
        'created_at': message.date.isoformat(),
    }
    result = requests.post(BACKEND_URL, json=payload, timeout=15).json()
    await message.answer(f"Задача создана: №{result['task_id']}. {result['message']}")


@dp.message(F.text)
async def text_handler(message: Message):
    payload = {
        'telegram_user_id': str(message.from_user.id),
        'username': message.from_user.username,
        'message_type': 'text',
        'text': message.text,
        'created_at': message.date.isoformat(),
    }
    result = requests.post(BACKEND_URL, json=payload, timeout=15).json()
    suffix = 'Требуется уточнение полей.' if result['requires_clarification'] else 'Все ключевые поля определены.'
    await message.answer(f"Задача создана: №{result['task_id']} — {suffix}")


if __name__ == '__main__':
    import asyncio
    asyncio.run(dp.start_polling(bot))
