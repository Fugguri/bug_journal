import inspect
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass, field, astuple, is_dataclass
from datetime import date, datetime

from storage.enums import Role, TicketType, TicketStatus
from utils.date import get_now_date


@dataclass
class Project:
    created_at: str = field(default=get_now_date())
    customer: str = field(default='')
    name: str = field(default='')
    description: str = field(default='')
    credentials_string: str = field(default='')
    tester_nickname: str = field(default='')
    dev_nickname: str = field(default='')
    deadline: str = field(default='')
    id: str | int = field(default='')

    def __str__(self):
        text = f"""<b>{self.name}</b>\n
Создан: <b>{self.created_at}</b>\n
Заказчик: <b>{self.customer}</b>\n
Описание: <b>{self.description}</b>\n
Доступы: <b>{self.credentials_string}</b>\n
Разработчик <b>@{self.dev_nickname}</b>\n
Тестировщик: <b>@{self.tester_nickname}</b>\n
Дата окончания: <b>{self.deadline}</b>"""
        return text


@dataclass
class User:
    name: str
    tg_username: str
    google_account: str
    comment: str


@dataclass
class Functionality:
    code: str = field(default='')
    description: str = field(default='')
    comment: str = field(default='')
    project_id: str = field(default='')


@dataclass
class Ticket:
    created_at: str = field(default='')
    functionality_code: str = field(default='')
    functionality_description: str = field(default='')
    functionality_comment: str = field(default='')
    functionality_project_id: str = field(default='')
    type: TicketType = field(default=TicketType.BUG)
    request_picture: str = field(default='')
    code_num: str = field(default='')
    tax: int = field(default=0)
    status: TicketStatus = field(default=TicketStatus.NEW)
    done_at: datetime = field(default='')
    checked_at: datetime = field(default='')
    payment_sum: int = field(default=0)

    def __str__(self):
        print(self.code_num)
        text = f'''<b>{self.type} №{self.code_num}</b>\n
Код проекта: <b>{self.functionality_project_id}</b>\n
Код ТЗ: <b>{self.functionality_code}</b>\n
Комментарий: <b>{self.functionality_comment}</b>\n
Описание: {self.functionality_description}'''
        return text


class Storage(metaclass=ABCMeta):
    def __new__(cls, *arg, **kwargs):
        parent_coros = inspect.getmembers(
            Storage, predicate=inspect.iscoroutinefunction)

        for coro in parent_coros:
            child_method = getattr(cls, coro[0])
            if not inspect.iscoroutinefunction(child_method):
                raise RuntimeError(
                    f'The method {child_method} must be a coroutine')

        return super(Storage, cls).__new__(cls, *arg, **kwargs)

    @abstractmethod
    async def add_project(self, project: Project) -> Project:
        pass

    @abstractmethod
    async def update_project(self, project: Project) -> Project:
        pass

    @abstractmethod
    async def delete_project(self, project: Project) -> Project:
        pass

    @abstractmethod
    async def get_project(self, name: str) -> Project:
        pass

    @abstractmethod
    async def get_all_projects(self) -> list[Project]:
        pass

    @abstractmethod
    async def add_ticket(self, ticket: Ticket) -> Ticket:
        pass

    @abstractmethod
    async def update_ticket(self, ticket: Ticket) -> Ticket:
        pass

    @abstractmethod
    async def delete_ticket(self, ticket: Ticket) -> Ticket:
        pass

    @abstractmethod
    async def get_ticket(self, request: str) -> Ticket:
        pass

    @abstractmethod
    async def get_project_tickets_by_name(self, project_name: str) -> list[Ticket]:
        pass

    @abstractmethod
    async def add_user(self, user: User) -> User:
        pass

    @abstractmethod
    async def update_user(self, user: User) -> User:
        pass

    @abstractmethod
    async def delete_user(self, user: User) -> User:
        pass

    @abstractmethod
    async def get_user(self, tg_usename: str) -> User:
        pass

    @abstractmethod
    async def get_all_users(self) -> list[User]:
        pass

    @staticmethod
    def get_dataclass_values(cls_or_instance) -> tuple:
        if is_dataclass(cls_or_instance):
            return astuple(cls_or_instance)
        raise TypeError(
            f"{cls_or_instance.__class__.__name__} is not a dataclass")
