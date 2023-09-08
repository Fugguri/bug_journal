from contextlib import suppress

from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardMarkup, InlineKeyboardMarkup, InputMediaPhoto
from loguru import logger

from bot.config import bot
from storage.types import User
from .users import get_user_by_id


async def delete_prev_message(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    with suppress(TelegramBadRequest):
        await bot.delete_message(message.chat.id, data['delete_msg_id'])


async def add_user_message_to_delete_list(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    messages = data.get('messages_to_delete_from_user', [])
    messages.append(message.message_id)
    await state.update_data(messages_to_delete_from_user=messages)


async def delete_user_messages(message: Message, state: FSMContext) -> None:
    logger.info('deleting user messages')
    data = await state.get_data()
    messages = data.get('messages_to_delete_from_user', [])
    logger.info(messages)
    with suppress(TelegramBadRequest):
        for msg_id in messages:
            await bot.delete_message(message.chat.id, msg_id)
    await state.update_data(messages_to_delete_from_user=[])


async def send_message_to_user(username: str, text: str = None,
                               reply_markup: InlineKeyboardMarkup | ReplyKeyboardMarkup = None,
                               media_group: list[InputMediaPhoto] = None) -> None:
    _, _, chat_id = await get_user_by_id(username)
    if media_group:
        await bot.send_media_group(chat_id, media_group)
    else:
        await bot.send_message(chat_id, text, reply_markup=reply_markup)
