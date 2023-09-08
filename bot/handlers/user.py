from aiogram import Router, F
from aiogram.filters import Command

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ContentType
from loguru import logger

from bot.utils.messages import delete_prev_message, add_user_message_to_delete_list
from bot.utils.users import get_user_by_id
from bot.keyboards.for_project import get_contact_keyboard
from bot.keyboards.reply import StartKeys
from bot.config import gsheets_storage
from utils.date import parse_date_from_string, get_now_date
from storage.types import User

router = Router()


class UserState(StatesGroup):
    entering_user = State()
    entering_google_account = State()
    entering_comment = State()


@router.message(Command(commands=['add_user']))
async def cmd_add_user(message: Message, state: FSMContext) -> None:
    await add_user_message_to_delete_list(message, state)
    await message.delete()
    msg = await message.answer('Выберите пользователя с помощью кнопки или введите username', reply_markup=get_contact_keyboard())
    await state.update_data(delete_msg_id=msg.message_id)
    await state.set_state(UserState.entering_user)


@router.message(UserState.entering_user,)
async def on_entering_user(message: Message, state: FSMContext) -> None:
    await delete_prev_message(message, state)
    await add_user_message_to_delete_list(message, state)
    if message.user_shared:
        first_name, username, _ = await get_user_by_id(message.user_shared.user_id)
    elif message.contact:
        first_name, username, _ = await get_user_by_id(message.contact.user_id)
    else:
        first_name, username, _ = await get_user_by_id(message.text)
    await state.update_data(user_first_name=first_name, user_username=username)
    msg = await message.answer('Введите гугл аккаунт пользователя')
    await state.update_data(delete_msg_id=msg.message_id)
    await state.set_state(UserState.entering_google_account)


@router.message(UserState.entering_google_account)
async def on_entering_google_account(message: Message, state: FSMContext) -> None:
    await delete_prev_message(message, state)
    await add_user_message_to_delete_list(message, state)
    await state.update_data(user_google_account=message.text)
    msg = await message.answer('Введите комментарий')
    await state.update_data(delete_msg_id=msg.message_id)
    await state.set_state(UserState.entering_comment)


@router.message(UserState.entering_comment)
async def on_entering_comment(message: Message, state: FSMContext) -> None:
    await delete_prev_message(message, state)
    await add_user_message_to_delete_list(message, state)
    comment = message.text
    data = await state.get_data()
    # data.pop('user_messages_to_delete')
    user_dict = {key: value for key,
                 value in data.items() if key.startswith('user_')}
    logger.debug(user_dict)
    user = User(*user_dict.values(), comment)
    try:
        await gsheets_storage.add_user(user)
        await message.answer(f'Пользователь {user.name} @{user.tg_username} успешно добавлен')
    except ValueError as ex:
        await message.answer(str(ex))
    await state.set_state(None)
