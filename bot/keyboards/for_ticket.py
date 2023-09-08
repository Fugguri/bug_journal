from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardMarkup, InlineKeyboardButton

from storage.types import Project, Ticket
from .callbacks import TicketTypeCallbackData, CancelCallbackData, ProjectNameCallbackData, Action, TicketCallbackData, TickerFunctionalityCode
from storage.enums import TicketType, Role


def get_ticket_type_keyboard(role: str = None) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    bug = TicketType.BUG
    changes = TicketType.CHANGES
    tz = TicketType.TZ
    if role == "owner":
        for ticket_type in TicketType:
            builder.add(InlineKeyboardButton(
                text=ticket_type, callback_data=TicketTypeCallbackData(type=ticket_type).pack()))
    elif role == "dev":
        pass
    elif role == "tester":
        builder.add(InlineKeyboardButton(
            text=bug, callback_data=TicketTypeCallbackData(type=bug).pack()))

    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)


def get_ticket_functionality_code(tickets: tuple | list) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for ticket in tickets:
        builder.add(InlineKeyboardButton(
            text=ticket.functionality_code, callback_data=TickerFunctionalityCode(code=ticket.functionality_code).pack()))

    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)


def get_cancel_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text='Нет картинки',
                callback_data=CancelCallbackData().pack()))
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)


def get_projects_keyboard(projects: list[Project]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for project in projects:
        builder.add(InlineKeyboardButton(text=project.name,
                                         callback_data=ProjectNameCallbackData(project_name=project.name).pack()))
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)


def get_ticket_keyboard(ticket: Ticket, project: Project, to_user_role: Role,
                        send_check_message: bool = False) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if to_user_role == Role.DEVELOPER:
        if send_check_message:
            builder.add(InlineKeyboardButton(
                text=Action.FIX,
                callback_data=TicketCallbackData(
                    action=Action.FIX, ticket_id=ticket.code_num, project_id=project.id, role="dev").pack()
            ))
        else:
            builder.add(InlineKeyboardButton(
                text=Action.ACCEPT,
                callback_data=TicketCallbackData(
                    action=Action.ACCEPT, ticket_id=ticket.code_num, project_id=project.id, role="dev").pack()
            ),
                InlineKeyboardButton(
                    text=Action.CANCEL,
                    callback_data=TicketCallbackData(
                        action=Action.CANCEL, ticket_id=ticket.code_num, project_id=project.id, role="dev").pack()
            ))

    if to_user_role == Role.TESTER:
        if send_check_message:
            builder.add(InlineKeyboardButton(
                text=Action.CHECK,
                callback_data=TicketCallbackData(
                    action=Action.CHECK, ticket_id=ticket.code_num, project_id=project.id, role="test").pack()
            ))
        else:
            builder.add(InlineKeyboardButton(
                text=Action.ACCEPT,
                callback_data=TicketCallbackData(
                    action=Action.ACCEPT, ticket_id=ticket.code_num, project_id=project.id, role="test").pack()
            ),
                InlineKeyboardButton(
                    text=Action.DECLINE,
                    callback_data=TicketCallbackData(
                        action=Action.DECLINE, ticket_id=ticket.code_num, project_id=project.id, role="test").pack()
            ),
                InlineKeyboardButton(
                    text=Action.CANCEL,
                    callback_data=TicketCallbackData(
                        action=Action.CANCEL, ticket_id=ticket.code_num, project_id=project.id, role="test").pack()
            )
            )
        builder.adjust(2)
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)
