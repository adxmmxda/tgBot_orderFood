import os

from aiogram import Bot, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.utils.callback_data import CallbackData
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.callback_data import CallbackData
from helper import create_inline_kb, create_reply_kb, find_menu_item_by_id, find_restoraunt_by_id
from content import RESTORAUNTS, MENU
from basket import Basket
from datetime import datetime

load_dotenv('.env.local')
GROUP_ID = -4254949432
bot = Bot(token=os.environ['BOT_TOKEN'], parse_mode='html')
dp = Dispatcher(bot, storage=MemoryStorage())

restoraunt_callback_data = CallbackData('restoraunt', 'id')
add_to_basket_callback_data = CallbackData('add_to_basket', 'menu_item_id')
order_callback_data = CallbackData('order')

basket = Basket()
users = ["Мехроч", "Мустафо", "Нодир", "Точвар", "Дилмурод"]


@dp.message_handler(
    content_types=[types.ContentType.TEXT],
    text='Заказать',
)
async def restoraunt_list_handler(message: types.Message) -> None:
    await bot.send_message(message.chat.id, 'Выберите категорию', reply_markup=create_inline_kb([
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

    await bot.send_message(call.message.chat.id, 'Меню {}'.format(restoraunt['name']))

    menu_items = [item for item in MENU if item['restoraunt_id'] == restoraunt['id']]

    for menu_item in menu_items:
        await bot.send_photo(
            call.message.chat.id,
            menu_item['picture_url'],
            caption="{} - {} сомони".format(menu_item['name'], menu_item['price']),
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


order_callback_data = CallbackData('order', 'action')

def create_inline_kb(buttons):
    kb = InlineKeyboardMarkup()
    for button in buttons:
        kb.add(InlineKeyboardButton(text=button['text'], callback_data=button['callback_data']))
    return kb

# Обработка корзины
async def show_basket_handler(message: types.Message) -> None:
    menu_item_id_to_quantity = basket.get_user_items(message.chat.id)

    if not menu_item_id_to_quantity:
        await bot.send_message(message.chat.id, 'Ваша корзина пуста')
        return
    
    await bot.send_message(message.chat.id, 'Вы добавили в корзину:')
    total_sum = 0

    for menu_item_id, quantity in menu_item_id_to_quantity.items():
        menu_item = find_menu_item_by_id(menu_item_id)
        restoraunt = find_restoraunt_by_id(menu_item['restoraunt_id'])
        item_total_price = quantity * menu_item['price']
        total_sum += item_total_price

        await bot.send_message(
            message.chat.id,
            '"{}" {} шт из категории "{}" на сумму {} сомони'.format(
                menu_item['name'],
                quantity,
                restoraunt['name'],
                item_total_price,
            ),
        )
    
    await bot.send_message(
        message.chat.id,
        'Итого: {} сомони'.format(total_sum),
        reply_markup=create_inline_kb([
            {
                'text': 'Оформить заказ',
                'callback_data': order_callback_data.new(action='confirm'),
            }
        ])
    )

# Обработка коллбеков для оформления заказа
@dp.callback_query_handler(order_callback_data.filter(action='confirm'))
async def confirm_order(call: types.CallbackQuery):
    # Получаем данные корзины пользователя
    menu_item_id_to_quantity = basket.get_user_items(call.message.chat.id)

    if not menu_item_id_to_quantity:
        await bot.send_message(call.message.chat.id, 'Ваша корзина пуста')
        await call.answer()
        return

    order_message = 'Новый заказ:\n'
    total_sum = 0

    for menu_item_id, quantity in menu_item_id_to_quantity.items():
        menu_item = find_menu_item_by_id(menu_item_id)
        restoraunt = find_restoraunt_by_id(menu_item['restoraunt_id'])
        item_total_price = quantity * menu_item['price']
        total_sum += item_total_price
        # отправка заказа в группу/
        order_message += '"{}" \n'.format(
            menu_item['name'],
            quantity,
            restoraunt['name'],
            item_total_price,
        )
    
    order_message += 'Итого: {} сомони. Заказ оформил {}'.format(total_sum, call.from_user.full_name)

    # Отправка заказа в группу
    await bot.send_message(GROUP_ID, order_message)
    
    # Уведомление пользователя
    await call.message.edit_text('Ваш заказ был отправлен на обработку.')
    await call.answer()

# Обработка команды /basket
@dp.message_handler(commands=['basket'])
async def basket_command_handler(message: types.Message):
    await show_basket_handler(message)


@dp.callback_query_handler(
    order_callback_data.filter(),
)
async def order_handler(call: types.CallbackQuery) -> None:
    basket.clear(call.message.chat.id)

    await bot.send_message(call.message.chat.id, 'Заказ принят')

@dp.message_handler(
    commands=['start'],
)
async def start_bot(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username
    full_name = message.from_user.full_name
    join_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Вывод информации о пользователе в терминал
    print(f'Пользователь {full_name} (@{username}, ID: {user_id}) нажал /start в {join_time}')
    await bot.send_message(
        message.chat.id,
        'Это бот для заказа еды',
        reply_markup=create_reply_kb([
            'Заказать',
            'Корзина',
        ]),
    )
@dp.message_handler(lambda message: message.text.lower() == 'корзина')
@dp.message_handler(commands=['basket'])
async def basket_command_handler(message: types.Message):
    await show_basket_handler(message)

async def on_startup(_) -> None:
    await bot.set_my_commands([
        types.BotCommand('start', 'Start bot')
    ])




executor.start_polling(dispatcher=dp, skip_updates=True, on_startup=on_startup)
