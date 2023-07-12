from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from typing import Any
from content import RESTORAUNTS, MENU


def chunks(lst: list[Any], n: int):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def create_inline_kb(items: list[dict], row_width: int = 1) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(one_time_keyboard=True)

    for chunk in chunks(items, row_width):
        row = []

        for i, item in enumerate(chunk):
            row.append(InlineKeyboardButton(text=item['text'], callback_data=item['callback_data']))

        kb.row(*row)

    return kb


def create_reply_kb(items: list[str], row_width: int = 1) -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(one_time_keyboard=False)

    for chunk in chunks(items, row_width):
        row = []

        for i, item in enumerate(chunk):
            row.append(KeyboardButton(text=item))

        kb.row(*row)

    return kb


def find_menu_item_by_id(menu_item_id: int) -> dict:
    return next(item for item in MENU if item['id'] == menu_item_id)



def find_restoraunt_by_id(restoraunt_id: int) -> dict:
    return next(rest for rest in RESTORAUNTS if rest['id'] == restoraunt_id)
