from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.types import KeyboardButtonRequestUser, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, \
    InlineKeyboardMarkup

from storage.enums import Role
from storage.types import User, Project
from .callbacks import AcceptProjectCallbackData, UserCallbackData, ProjectCallbackData


def get_contact_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(
        text='Выбрать',
        request_user=KeyboardButtonRequestUser(request_id=1, user_is_bot=False)
    ))
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)


def get_accept_project_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(
        text='Согласен',
        callback_data=AcceptProjectCallbackData().pack()
    ))
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)


def get_users_keyboard(users: list[User], role: Role) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for user in users:
        builder.add(InlineKeyboardButton(
            text=f"{user.name} @{user.tg_username}",
            callback_data=UserCallbackData(username=user.tg_username, role=role).pack()
        ))
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)


def get_project_keyboard(project: Project) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(
        text='Добавить тикет',
        callback_data=ProjectCallbackData(project_id=str(project.id)).pack()
    ))
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)


def get_projects_keyboard(projects: list[Project]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for project in projects:
        builder.add(InlineKeyboardButton(
            text=project.name,
            callback_data=ProjectCallbackData(project_id=project.id).pack()
        ))
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)
