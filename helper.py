from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from typing import Any


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
