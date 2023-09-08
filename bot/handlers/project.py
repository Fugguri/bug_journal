from dataclasses import astuple

from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
from loguru import logger

from bot.config import gsheets_storage
from bot.keyboards.callbacks import UserCallbackData, AcceptProjectCallbackData
from bot.keyboards.for_project import get_accept_project_keyboard, get_users_keyboard, get_project_keyboard, get_projects_keyboard
from bot.utils.messages import delete_prev_message, send_message_to_user, delete_user_messages, \
    add_user_message_to_delete_list
from storage.enums import Role
from storage.types import Project, User
from utils.date import parse_date_from_string, get_now_date

router = Router()


@router.message(Command(commands=['clear']))
async def cmd_clear(message: Message, state: FSMContext) -> None:
    await state.set_state(None)


class ProjectState(StatesGroup):
    entering_name = State()
    entering_description = State()
    entering_credentials = State()
    entering_dev = State()
    entering_tester = State()
    entering_deadline = State()





@router.message(Command(commands=['add_project']))
async def cmd_add_project(message: Message, state: FSMContext) -> None:
    await message.delete()
    users = await gsheets_storage.get_all_users()
    if not users:
        msg = await message.answer('Вы еще не добавили ни одного пользователя. Для этого нажмите /add_user')
        await state.update_data(delete_msg_id=msg.message_id)
        return
    await state.update_data(users=[astuple(user) for user in users])
    msg = await message.answer('Введите краткое название проекта')
    await state.update_data(delete_msg_id=msg.message_id)
    await state.set_state(ProjectState.entering_name)


@router.message(ProjectState.entering_name)
async def on_entering_name(message: Message, state: FSMContext) -> None:
    await delete_prev_message(message, state)
    await add_user_message_to_delete_list(message, state)
    if len(message.text) > 6:
        msg = await message.answer('Название содержит более 6 символов. Пожалуйста, попробуйте снова')
        await state.update_data(delete_msg_id=msg.message_id)
        return
    if len(message.text.split(' ')) > 1:
        msg = await message.answer('Название содержит пробелы. Пожалуйста, повторите снова')
        await state.update_data(delete_msg_id=msg.message_id)
        return
    msg = await message.answer('Введите описание проекта')
    await state.update_data(project_name=message.text)
    await state.update_data(delete_msg_id=msg.message_id)
    await state.set_state(ProjectState.entering_description)


@router.message(ProjectState.entering_description)
async def on_entering_description(message: Message, state: FSMContext) -> None:
    await delete_prev_message(message, state)
    await add_user_message_to_delete_list(message, state)
    msg = await message.answer('Введите доступы, нужные для проекта')
    await state.update_data(project_description=message.text)
    await state.update_data(delete_msg_id=msg.message_id)
    await state.set_state(ProjectState.entering_credentials)


@router.message(ProjectState.entering_credentials)
async def on_entering_credentials(message: Message, state: FSMContext) -> None:
    await delete_prev_message(message, state)
    await add_user_message_to_delete_list(message, state)
    await state.update_data(project_credentials=message.text)
    data = await state.get_data()
    users = data.get('users')
    users = [User(*values) for values in users]
    msg = await message.answer('Выберите разработчика проекта', reply_markup=get_users_keyboard(users, Role.DEVELOPER))
    await state.update_data(delete_msg_id=msg.message_id)
    await state.update_data(users=[astuple(user) for user in users])


@router.callback_query(UserCallbackData.filter())
async def on_entering_user(query: CallbackQuery, callback_data: UserCallbackData, state: FSMContext) -> None:
    logger.debug('handle user')
    await delete_prev_message(query.message, state)
    username = callback_data.username
    if callback_data.role == Role.DEVELOPER:
        data = await state.get_data()
        users = [User(*user_data) for user_data in data.get('users')]
        await query.answer()
        msg = await query.message.answer('Выберите тестировщика проекта',
                                         reply_markup=get_users_keyboard(users, Role.TESTER))
        await state.update_data(delete_msg_id=msg.message_id, users=[])
    await state.update_data({f'project_{callback_data.role}': username.strip('@')})
    await query.answer()
    if callback_data.role == Role.TESTER:
        msg = await query.message.answer('Введите дату окончания проекта в формате дд.мм.гггг')
        await state.update_data(delete_msg_id=msg.message_id)
        await state.set_state(ProjectState.entering_deadline)


@router.message(ProjectState.entering_deadline)
async def on_entering_deadline(message: Message, state: FSMContext) -> None:
    await delete_prev_message(message, state)
    await add_user_message_to_delete_list(message, state)
    try:
        date = parse_date_from_string(message.text)
    except ValueError:
        msg = await message.answer('Неверный формат даты. Пожалуйста, повторите снова', )
        await state.update_data(delete_msg_id=msg.message_id)
        return
    data = await state.get_data()
    # data.pop('project_dev')
    # data.pop('project_tester')
    # data.pop('project_last_id')
    project_data = {key: value for key, value in data.items() if key.startswith('project')}
    logger.debug(project_data)
    project = Project(get_now_date(), message.from_user.username, *project_data.values(), date.strftime('%d.%m.%Y'),)
    logger.debug(project)
    project = await gsheets_storage.add_project(project)
    await state.set_state(None)
    await state.update_data(last_id=project.id)
    await message.answer(f"Создан проект {str(project)}", reply_markup=get_project_keyboard(project))
    for user in (project.dev_nickname, project.tester_nickname):
        await send_message_to_user(user, f'Создан проект {str(project)}',
                                   get_accept_project_keyboard())
    await delete_user_messages(message, state)


@router.callback_query(AcceptProjectCallbackData.filter())
async def on_accept_project(query: CallbackQuery, callback_data: AcceptProjectCallbackData, state: FSMContext) -> None:
    await query.message.delete()
