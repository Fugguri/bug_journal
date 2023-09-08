from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery, InputMediaPhoto, FSInputFile
from loguru import logger

from bot.config import gsheets_storage, bot
from bot.keyboards.callbacks import TicketTypeCallbackData, CancelCallbackData, ProjectNameCallbackData, \
    ProjectCallbackData, TicketCallbackData, Action, TickerFunctionalityCode
from bot.keyboards.for_ticket import get_ticket_type_keyboard, get_cancel_keyboard, get_ticket_keyboard, get_ticket_functionality_code
from bot.keyboards.for_project import get_projects_keyboard
from bot.utils.messages import delete_prev_message, add_user_message_to_delete_list, send_message_to_user
from storage.enums import Role, TicketStatus, TicketType
from storage.types import Ticket, Project
from utils import BASE_DIR

from utils.date import get_now_datetime

router = Router()


class TicketState(StatesGroup):
    entering_functionality_code: str = State()
    entering_functionality_description: str = State()
    entering_functionality_comment: str = State()
    entering_request_pic = State()
    entering_status = State()


@router.message(Command(commands=['list_projects']))
async def cmd_list_projects(message: Message, state: FSMContext) -> None:
    projects = await gsheets_storage.get_all_projects()
    await state.clear()
    msg = await message.answer('Выберите проект', reply_markup=get_projects_keyboard(projects))


def create_role(username: str, project: Project) -> str:
    if username == project.customer:
        return "owner"
    elif username == project.dev_nickname.replace("@", ""):
        return "dev"
    elif username == project.tester_nickname.replace("@", ""):
        return "tester"
    else:
        return "owner"


@router.callback_query(ProjectCallbackData.filter())
async def on_add_ticket(query: CallbackQuery, callback_data: ProjectCallbackData, state: FSMContext) -> None:
    await state.update_data(_project_id=callback_data.project_id)
    project: Project = await gsheets_storage.get_project_by_id(callback_data.project_id)
    role = create_role(query.from_user.username, project)
    await state.update_data(user_role=role)
    if role == "guest":
        projects = await gsheets_storage.get_all_projects()
        await state.clear()
        await query.message.delete()
        msg = await query.message.answer("У вас нет доступа к этому проекту,выберите другой", reply_markup=get_projects_keyboard(projects))
        return
    msg = await query.message.answer(str(project), reply_markup=get_ticket_type_keyboard(role))
    await state.update_data(delete_msg_id=msg.message_id)
    await state.update_data(ticket_project_id=callback_data.project_id)
    await state.set_state(TicketState.entering_functionality_description)

    # msg = await query.message.answer('Введите код функционала')
    # await query.message.delete()
    # await state.set_state(TicketState.entering_functionality_code)
    # TicketState.entering_functionality_code
    # await state.update_data(delete_msg_id=msg.message_id)


@router.callback_query(TicketTypeCallbackData.filter())
async def on_project_name(query: CallbackQuery, state: FSMContext, callback_data: TicketTypeCallbackData) -> None:
    await state.update_data(ticket_type=callback_data.type)
    data = await state.get_data()
    project_id = data['_project_id']

    if callback_data.type == "ТЗ":
        msg = await query.message.answer('Введите код функционала')
        await query.message.delete()
        await state.set_state(TicketState.entering_functionality_code)
        await state.update_data(delete_msg_id=msg.message_id)
        return
    tickets_codes = await gsheets_storage.get_project_cunctionality_id(project_id)
    if not tickets_codes:
        role = data['user_role']
        msg = await query.message.answer('Сначала добавьте техническое задание', reply_markup=get_ticket_type_keyboard(role))
    else:
        msg = await query.message.answer('Выберите код Технического задания', reply_markup=get_ticket_functionality_code(tickets_codes))
    await add_user_message_to_delete_list(query.message, state)
    await delete_prev_message(query.message, state)
    # await state.update_data(ticket_functionality_code=query.text)
    await state.update_data(delete_msg_id=msg.message_id)
    await state.set_state(TicketState.entering_functionality_description)


@router.callback_query(TickerFunctionalityCode.filter())
async def on_project_name(query: CallbackQuery, state: FSMContext, callback_data: TicketTypeCallbackData) -> None:
    await add_user_message_to_delete_list(query.message, state)
    await delete_prev_message(query.message, state)
    msg = await query.message.answer('Введите комментарий')
    await state.update_data(ticket_functionality_code=callback_data.code)
    await state.update_data(ticket_functionality_description='')
    await state.update_data(delete_msg_id=msg.message_id)
    await state.set_state(TicketState.entering_functionality_comment)


@router.message(TicketState.entering_functionality_code)
async def on_project_name(message: Message, state: FSMContext) -> None:
    await add_user_message_to_delete_list(message, state)
    await delete_prev_message(message, state)
    msg = await message.answer('Введите описание функционала')
    await state.update_data(ticket_functionality_code=message.text)
    await state.update_data(delete_msg_id=msg.message_id)
    await state.set_state(TicketState.entering_functionality_description)


@router.message(TicketState.entering_functionality_description)
async def on_entering_description(message: Message, state: FSMContext) -> None:
    await add_user_message_to_delete_list(message, state)
    await delete_prev_message(message, state)
    msg = await message.answer('Введите комментарий')
    await state.update_data(ticket_functionality_description=message.text)
    await state.update_data(delete_msg_id=msg.message_id)
    await state.set_state(TicketState.entering_functionality_comment)


@router.message(TicketState.entering_functionality_comment)
async def on_entering_comment(message: Message, state: FSMContext) -> None:
    await add_user_message_to_delete_list(message, state)
    await delete_prev_message(message, state)
    await state.update_data(ticket_functionality_comment=message.text)
    msg = await message.answer(
        'Вставьте картинку (скрин экрана с пометками), или, если картинки не будет, то нажмите на кнопку ниже',
        reply_markup=get_cancel_keyboard())
    await state.update_data(delete_msg_id=msg.message_id)
    await state.set_state(TicketState.entering_request_pic)


@router.message(TicketState.entering_request_pic)
async def on_entering_request_pic(message: Message, state: FSMContext) -> None:
    await delete_prev_message(message, state)
    await add_user_message_to_delete_list(message, state)
    if not message.photo:
        msg = await message.answer('Кажется, вы не отправили фото. Пожалуйста, попробуйте снова.\nЕсли картинки не будет, то нажмите на кнопку ниже', reply_markup=get_cancel_keyboard())
        await state.update_data(delete_msg_id=msg.message_id)
        return
    filepath = BASE_DIR / 'photos' / f'{message.photo[-1].file_id}.jpg'
    await bot.download(message.photo[-1], destination=filepath)
    image_link = gsheets_storage.upload_image_to_drive(filepath)
    image = f'=IMAGE("{image_link}";4;250;250)'
    await state.update_data(ticket_pic=image)
    await _add_ticket(message, state, filepath)


@router.callback_query(CancelCallbackData.filter())
async def on_cancel(query: CallbackQuery, state: FSMContext) -> None:
    await add_user_message_to_delete_list(query.message, state)
    await delete_prev_message(query.message, state)
    await state.update_data(ticket_pic='')
    await _add_ticket(query.message, state)


async def _add_ticket(message: Message, state: FSMContext, photo_path: str = None) -> None:
    data = await state.get_data()
    data = {key: value for key, value in data.items() if key.startswith('ticket')}
    project = await gsheets_storage.get_project(data['ticket_project_id'])
    await delete_prev_message(message, state)
    await state.set_state(None)
    logger.debug(data.values())
    ticket = Ticket(get_now_datetime(),
                    functionality_code=data['ticket_functionality_code'],
                    functionality_description=data['ticket_functionality_description'],
                    functionality_comment=data['ticket_functionality_comment'],
                    functionality_project_id=data['ticket_project_id'],
                    type=data['ticket_type'],
                    request_picture=data['ticket_pic'],)
    ticket = await gsheets_storage.add_ticket(ticket)
    # msg = await message.answer(f'Добавлена заявка {str(ticket)}')
    # await state.update_data(delete_msg_id=msg.message_id)
    if photo_path:
        photo = InputMediaPhoto(media=FSInputFile(
            path=photo_path), caption=f'Создана заявка: \n{str(ticket)}')
        await send_message_to_user(project.dev_nickname, media_group=[photo],
                                   reply_markup=get_ticket_keyboard(ticket, project, Role.DEVELOPER, send_check_message=True))
        await send_message_to_user(project.customer, media_group=[photo])
    else:
        await send_message_to_user(project.dev_nickname, f'Создана заявка: \n{str(ticket)}',
                                   reply_markup=get_ticket_keyboard(ticket, project, Role.DEVELOPER, send_check_message=True))
        await send_message_to_user(project.customer, f'Создана заявка: \n{str(ticket)}')


@router.callback_query(TicketCallbackData.filter(F.action == Action.FIX))
async def on_fix(query: CallbackQuery, callback_data: TicketCallbackData) -> None:
    ticket = await gsheets_storage.get_ticket(callback_data.ticket_id, callback_data.project_id)
    project = await gsheets_storage.get_project(callback_data.project_id)
    # await query.message.delete()
    await query.message.answer('Вы точно исправили глюк / правки?',
                               reply_markup=get_ticket_keyboard(ticket, project, to_user_role=Role.DEVELOPER))


@router.callback_query(TicketCallbackData.filter(F.action == Action.CHECK))
async def on_check(query: CallbackQuery, callback_data: TicketCallbackData) -> None:
    ticket = await gsheets_storage.get_ticket(callback_data.ticket_id, callback_data.project_id)
    project = await gsheets_storage.get_project(callback_data.project_id)
    await query.message.answer('Вы точно протестировали глюк / правки?',
                               reply_markup=get_ticket_keyboard(ticket, project, to_user_role=Role.TESTER))


@router.callback_query(TicketCallbackData.filter(F.action == Action.DECLINE))
async def on_decline(query: CallbackQuery, callback_data: TicketCallbackData) -> None:
    ticket = await gsheets_storage.get_ticket(callback_data.ticket_id, callback_data.project_id)
    project = await gsheets_storage.get_project(callback_data.project_id)
    ticket.status = TicketStatus.NOT_DONE
    ticket.checked_at = get_now_datetime()
    await gsheets_storage.update_ticket(ticket)
    await query.message.delete()
    await query.message.answer(f'Заявка отправлена на доработку: \n{str(ticket)}',
                               reply_markup=get_ticket_keyboard(ticket, project, Role.DEVELOPER, send_check_message=True))


@router.callback_query(TicketCallbackData.filter(F.action == Action.ACCEPT))
async def on_accept(query: CallbackQuery, callback_data: TicketCallbackData) -> None:
    ticket = await gsheets_storage.get_ticket(callback_data.ticket_id, callback_data.project_id)
    if callback_data.role == "dev":
        project = await gsheets_storage.get_project(callback_data.project_id)
        ticket.status = TicketStatus.DONE
        await gsheets_storage.update_ticket(ticket)
        await send_message_to_user(project.tester_nickname, f'Заявка: \n{str(ticket)}',
                                   reply_markup=get_ticket_keyboard(ticket, project, Role.TESTER, send_check_message=True))
        return

    elif callback_data.role == "test":
        ticket.status = TicketStatus.APPROVED
        ticket.checked_at = get_now_datetime()
        ticket.done_at = get_now_datetime()
        await gsheets_storage.update_ticket(ticket)
    await query.message.delete()


@router.callback_query(TicketCallbackData.filter(F.action == Action.CANCEL))
async def on_cancel(query: CallbackQuery, callback_data: TicketCallbackData) -> None:
    await query.message.delete()
