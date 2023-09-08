from enum import StrEnum

from aiogram.utils.keyboard import CallbackData

from storage.enums import TicketType, Role
from dataclasses import field


class Action(StrEnum):
    FIX = 'Исправил'
    CHECK = 'Проверил'
    ACCEPT = 'Да'
    DECLINE = 'НЕ исправлено'
    CANCEL = 'Отмена'


class TicketTypeCallbackData(CallbackData, prefix='ticket_type'):
    type: TicketType | str


class CancelCallbackData(CallbackData, prefix='ticket_pic_cancel'):
    pass


class TickerFunctionalityCode(CallbackData, prefix='ticket_functionality_code'):
    code: str


class ProjectNameCallbackData(CallbackData, prefix='ticket_project_name'):
    project_name: str


class AcceptProjectCallbackData(CallbackData, prefix='accept_project'):
    pass


class UserCallbackData(CallbackData, prefix='user'):
    username: str
    role: Role


class ProjectCallbackData(CallbackData, prefix='functionality'):
    project_id: str


class TicketCallbackData(CallbackData, prefix='ticket'):
    action: Action
    ticket_id: str
    project_id: str
    role: str = field(default='')
