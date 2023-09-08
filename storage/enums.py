from enum import StrEnum


class Role(StrEnum):
    CUSTOMER = 'Заказчик'
    DEVELOPER = 'Программист'
    TESTER = 'Тестировщик'


class TicketType(StrEnum):
    BUG = 'Глюк'
    CHANGES = 'Правки'
    TZ = 'ТЗ'


class TicketStatus(StrEnum):
    NEW = 'Новая'
    DONE = 'Сделано'
    NOT_DONE = 'Не сделано'
    APPROVED = 'Проверено'
