import os

from aiogram import Bot, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from dotenv import load_dotenv

load_dotenv('.env.local')

bot = Bot(token=os.environ['BOT_TOKEN'], parse_mode='html')
dp = Dispatcher(bot, storage=MemoryStorage())


@dp.message_handler(
    content_types=[types.ContentType.TEXT],
    regexp='^[^/]+',
)
async def message_handler(message: types.Message) -> None:
    await bot.send_message(message.chat.id, message.text)


@dp.message_handler(
    commands=['start'],
)
async def start_bot(message: types.Message):
    await bot.send_message(
        message.chat.id,
        'Это эхо-бот, напиши мне что-нибудь!',
    )


executor.start_polling(dispatcher=dp, skip_updates=True)
