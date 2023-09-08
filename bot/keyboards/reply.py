from enum import StrEnum

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder


class StartKeys(StrEnum):
    add_user = "/add_user"
    add_profect = "/add_project"
    add_ticket = "/add_ticket"
    list_project = "/list_projects"


def get_start_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text=StartKeys.add_user))
    # builder.add(KeyboardButton(text=StartKeys.add_ticket))
    builder.add(KeyboardButton(text=StartKeys.add_profect))
    builder.add(KeyboardButton(text=StartKeys.list_project))
    return builder.as_markup(resize_keyboard=True)
