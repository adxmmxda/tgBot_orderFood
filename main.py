import os

from aiogram import Bot, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.utils.callback_data import CallbackData
from dotenv import load_dotenv

from helper import create_inline_kb, create_reply_kb, find_menu_item_by_id, find_restoraunt_by_id
from content import RESTORAUNTS, MENU
from basket import Basket

load_dotenv('.env.local')

bot = Bot(token=os.environ['BOT_TOKEN'], parse_mode='html')
dp = Dispatcher(bot, storage=MemoryStorage())

restoraunt_callback_data = CallbackData('restoraunt', 'id')
add_to_basket_callback_data = CallbackData('add_to_basket', 'menu_item_id')
order_callback_data = CallbackData('order')

basket = Basket()


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
    restoraunt = find_restoraunt_by_id(int(callback_data['id']))

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


@dp.callback_query_handler(
    add_to_basket_callback_data.filter(),
)
async def add_to_basket_handler(call: types.CallbackQuery, callback_data: dict) -> None:
    menu_item = find_menu_item_by_id(int(callback_data['menu_item_id']))

    basket.add(call.message.chat.id, menu_item['id'])
    await bot.send_message(call.message.chat.id, 'Добавили {} в вашу корзину'.format(menu_item['name']))

    await call.answer()


@dp.message_handler(
    content_types=[types.ContentType.TEXT],
    text='Корзина',
)
async def show_basket_handler(message: types.Message) -> None:
    menu_item_id_to_quantity = basket.get_user_items(message.chat.id)

    if menu_item_id_to_quantity == {}:
        await bot.send_message(message.chat.id, 'Ваша корзина пуста')
        return
    
    await bot.send_message(message.chat.id, 'Вы добавили в корзину:')
    total_sum = 0

    for menu_item_id in menu_item_id_to_quantity.keys():
        menu_item = find_menu_item_by_id(menu_item_id)
        restoraunt = find_restoraunt_by_id(menu_item['restoraunt_id'])
        quantity = menu_item_id_to_quantity[menu_item_id]
        item_total_price = quantity * menu_item['price']
        total_sum += item_total_price

        await bot.send_message(
            message.chat.id,
            '"{}" {} шт из ресторана "{}" на сумму {} руб'.format(
                menu_item['name'],
                quantity,
                restoraunt['name'],
                item_total_price,
            ),
        )
    
    await bot.send_message(message.chat.id, 'Итого: {} руб'.format(total_sum), reply_markup=create_inline_kb([
        {
            'text': 'Оформить заказ',
            'callback_data': order_callback_data.new(),
        }
    ]))


@dp.callback_query_handler(
    order_callback_data.filter(),
)
async def order_handler(call: types.CallbackQuery) -> None:
    basket.clear(call.message.chat.id)

    await bot.send_message(call.message.chat.id, 'Спасибо за ваш заказ, наш менеджер свяжется с вами в ближайшее время')

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
