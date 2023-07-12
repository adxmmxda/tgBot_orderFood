import os

from aiogram import Bot, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.utils.callback_data import CallbackData
from dotenv import load_dotenv

from helper import create_inline_kb, create_reply_kb
from content import RESTORAUNTS, MENU

load_dotenv('.env.local')

bot = Bot(token=os.environ['BOT_TOKEN'], parse_mode='html')
dp = Dispatcher(bot, storage=MemoryStorage())

restoraunt_callback_data = CallbackData('restoraunt', 'id')
add_to_basket_callback_data = CallbackData('add_to_basket', 'menu_item_id')


@dp.message_handler(
    content_types=[types.ContentType.TEXT],
    text='Рестораны',
)
async def restoraunt_list_handler(message: types.Message) -> None:
    await bot.send_message(message.chat.id, 'Выберите ресторан', reply_markup=create_inline_kb([
        {
            'text': restoraunt['name'],
            'callback_data': restoraunt_callback_data.new(id=restoraunt['id']),
        }
        for restoraunt in RESTORAUNTS
    ]))


@dp.callback_query_handler(
    restoraunt_callback_data.filter(),
)
async def restoraunt_handler(call: types.CallbackQuery, callback_data: dict) -> None:
    restoraunt = next(rest for rest in RESTORAUNTS if rest['id'] == int(callback_data['id']))

    await bot.send_message(call.message.chat.id, 'Меню ресторана {}'.format(restoraunt['name']))

    menu_items = [item for item in MENU if item['restoraunt_id'] == restoraunt['id']]

    for menu_item in menu_items:
        await bot.send_photo(
            call.message.chat.id,
            menu_item['picture_url'],
            caption="{} - {} руб".format(menu_item['name'], menu_item['price']),
            reply_markup=create_inline_kb([
                {
                    'text': 'Добавить в корзину',
                    'callback_data': add_to_basket_callback_data.new(menu_item_id=menu_item['id']),
                },
            ])
        )

    await call.answer()


@dp.message_handler(
    content_types=[types.ContentType.TEXT],
    text='Корзина',
)
async def message_handler(message: types.Message) -> None:
    await bot.send_message(message.chat.id, 'Ваша корзина пуста')


@dp.message_handler(
    commands=['start'],
)
async def start_bot(message: types.Message):
    await bot.send_message(
        message.chat.id,
        'Это бот для заказа еды из ресторанов',
        reply_markup=create_reply_kb([
            'Рестораны',
            'Корзина',
        ]),
    )


async def on_startup(_) -> None:
    await bot.set_my_commands([
        types.BotCommand('start', 'Start bot')
    ])


executor.start_polling(dispatcher=dp, skip_updates=True, on_startup=on_startup)
