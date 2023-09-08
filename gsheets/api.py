import re
from pathlib import Path

from gspread_asyncio import AsyncioGspreadWorksheet
from loguru import logger

from storage.enums import TicketType, TicketStatus
from storage.types import Storage, Ticket, Project, User
from ._connection import get_sheet_by_title, delete_sheet, add_sheet, drive


class GSheetsStorage(Storage):
    def __init__(self):
        self.__projects_sheets: dict[str, AsyncioGspreadWorksheet] = {}

    async def add_project(self, project: Project) -> Project:
        # _, project_row_num = await self.get_project_row(last=True)
        projects_sheet = await self._get_projects_sheet()
        project.id = await self._get_next_id()
        project_values = self.get_dataclass_values(project)
        await projects_sheet.append_row(list(project_values))
        return project

    async def update_project(self, project: Project) -> Project:
        projects_sheet = await self._get_projects_sheet()
        project_values = self.get_dataclass_values(project)
        project_row, row_num = await self.get_project_row(project.name)
        await projects_sheet.delete_rows(row_num, row_num)
        await projects_sheet.append_row(list(project_values))
        return project

    async def delete_project(self, project: Project) -> Project:
        projects_sheet = await self._get_projects_sheet()
        _, row_num = await self.get_project_row(project.name)
        await projects_sheet.delete_rows(row_num, row_num)
        await delete_sheet(self.__projects_sheets[project.name])
        self.__projects_sheets.pop(project.name)
        return project

    async def get_project(self, name: str) -> Project:
        row, _ = await self.get_project_row(name)
        return Project(*row)

    async def get_project_by_id(self, id: str) -> Project:
        row, _ = await self.get_project_row(project_id=id)
        return Project(*row)

    async def get_project_cunctionality_id(self, id: str) -> Project:
        rows = await self.get_all_ticket_row_by_id(project_id=id)
        res = []
        for row in rows:
            res.append(Ticket(*row[0]))
        return res

    async def get_all_projects(self) -> list[Project]:
        projects = []
        projects_sheet = await self._get_projects_sheet()
        rows_count = projects_sheet.row_count
        for row in range(2, rows_count + 1):
            row_values = await projects_sheet.row_values(row)
            logger.debug(row_values)
            if not row_values:
                break
            project = Project(*row_values)
            projects.append(project)
        return projects

    async def _get_next_id(self) -> int | str:
        projects_sheet = await self._get_projects_sheet()
        rows_count = projects_sheet.row_count
        for row in range(2, rows_count + 1):
            row_values = await projects_sheet.row_values(row)
            logger.debug(row_values)
            if not row_values:
                return row - 1

    async def add_ticket(self, ticket: Ticket) -> Ticket:
        prefixes = {TicketType.TZ: '1',
                    TicketType.BUG: '4', TicketType.CHANGES: '7'}
        ticket_code_num = await self._get_ticket_new_id(ticket, prefixes[ticket.type])
        sheet = await get_sheet_by_title('Журнал')
        ticket.code_num = ticket_code_num
        tax = 0
        if ticket.type == TicketType.CHANGES:
            tax = 150
        ticket.tax = tax
        ticket.status = TicketStatus.NEW

        ticket_values = self.get_dataclass_values(ticket)
        await sheet.append_row(list(ticket_values), value_input_option='USER_ENTERED')
        return ticket

    async def update_ticket(self, ticket: Ticket) -> Ticket:
        ticket_values = self.get_dataclass_values(ticket)
        _, row_num = await self.get_ticket_row(ticket.code_num)
        sheet = await get_sheet_by_title('Журнал')
        await sheet.delete_rows(row_num, row_num)
        await sheet.append_row(list(ticket_values))
        return ticket

    async def delete_ticket(self, ticket: Ticket) -> Ticket:
        _, row_num = await self.get_ticket_row(ticket.code_num)
        sheet = await get_sheet_by_title('Журнал')
        await sheet.delete_rows(row_num, row_num)
        return ticket

    async def get_ticket(self, code_num: str, project_id: str = None) -> Ticket:
        if project_id:
            sheet = await get_sheet_by_title('Журнал')
            cells = await sheet.findall(project_id)
            print(cells)
            for cell in cells:
                row_values = await sheet.row_values(cell.row)
                print(row_values)
                if row_values[1] != code_num:
                    continue
            return Ticket(*row_values)

        row, _ = await self.get_ticket_row(code_num)
        return Ticket(*row)

    async def get_project_tickets_by_name(self, project_name: str) -> list[Ticket]:
        tickets = []
        project_row = await self.get_project_row(project_name)
        project_id = project_row[-1]
        sheet = await get_sheet_by_title('Журнал')
        cells = await sheet.findall(project_id)
        for cell in cells:
            row_values = await sheet.row_values(cell.row)
            if not row_values:
                break
            ticket = Ticket(*row_values)
            tickets.append(ticket)
        return tickets

    @staticmethod
    async def _get_ticket_new_id(ticket: Ticket, prefix: str) -> str:
        criteria = re.compile(rf"{prefix}\d\d\d")
        max_id = 1
        sheet = await get_sheet_by_title('Журнал')
        cells = await sheet.findall(criteria)
        if not cells:
            return f"{prefix}001"
        for cell in cells:
            row = await sheet.row_values(cell.row)
            if row[4] == ticket.functionality_project_id:
                last_id = int(row[7][1:])
                if last_id >= max_id:
                    last_id += 1
                    max_id = last_id
        new_id = f"{prefix}{max_id:03}"
        return new_id

    @staticmethod
    async def get_project_row(project_name: str = None,  last: bool = False, project_id: str = None,) -> tuple[list, int]:
        logger.debug('getting project row')
        projects_sheet = await GSheetsStorage._get_projects_sheet()
        row, row_num = [], 0
        if not last:
            if project_name:
                cell = await projects_sheet.find(project_name)
            elif project_id:
                cell = await projects_sheet.find(project_id)
            row, row_num = await projects_sheet.row_values(cell.row), cell.row
        else:
            for row in range(2, projects_sheet.row_count + 1):
                if not row:
                    break
                row, row_num = await projects_sheet.row_values(row), row
        return row, row_num

    @staticmethod
    async def get_ticket_row(code_num: str,) -> tuple[list, int]:
        sheet = await get_sheet_by_title('Журнал')
        cell = await sheet.find(code_num)
        row_num = cell.row
        return await sheet.row_values(row_num), row_num

    @staticmethod
    async def get_all_ticket_row_by_id(project_id: str) -> tuple[list, int]:
        sheet = await get_sheet_by_title('Журнал')
        cells = await sheet.findall(project_id)
        res = []
        for cell in cells:
            row_num = cell.row
            res.append((await sheet.row_values(row_num), row_num))
        return res

    @staticmethod
    async def _get_projects_sheet() -> AsyncioGspreadWorksheet:
        return await get_sheet_by_title('Проекты')

    @staticmethod
    def upload_image_to_drive(file: Path) -> str:
        f = drive.CreateFile({'title': file.name})
        f.SetContentFile(str(file.absolute().resolve()))
        f.Upload()
        f.InsertPermission(
            {'type': 'anyone', 'value': 'anyone', 'role': 'reader'})
        f.Upload()
        return f'https://drive.google.com/uc?export=view&id={f["id"]}'

    async def add_user(self, user: User) -> User:
        row = await self.get_user_row(user.tg_username)
        if row[0] != [] and row[1] != 0:
            raise ValueError('Такой юзер уже есть в системе')
        user_values = self.get_dataclass_values(user)
        sheet = await self._get_users_sheet()
        await sheet.append_row(list(user_values), value_input_option='USER_ENTERED')
        return user

    async def update_user(self, user: User) -> User:
        user_values = self.get_dataclass_values(user)
        _, row_num = await self.get_user_row(user.tg_username)
        sheet = await self._get_users_sheet()
        await sheet.delete_rows(row_num, row_num)
        await sheet.append_row(list(user_values))
        return user

    async def delete_user(self, user: User) -> User:
        _, row_num = await self.get_user_row(user.tg_username)
        sheet = await self._get_users_sheet()
        await sheet.delete_rows(row_num, row_num)
        return user

    async def get_user(self, tg_usename: str) -> User:
        row, _ = self.get_user_row(tg_usename)
        return User(*row)

    async def get_all_users(self) -> list[User]:
        users = []
        users_sheet = await self._get_users_sheet()
        rows_count = users_sheet.row_count
        for row in range(2, rows_count + 1):
            row_values = await users_sheet.row_values(row)
            if not row_values:
                break
            logger.debug(row_values)
            user = User(*row_values)
            users.append(user)
        return users

    async def get_user_row(self, tg_username: str) -> tuple[list, int]:
        sheet = await self._get_users_sheet()

        row, row_num = [], 0
        cell = await sheet.find(tg_username)
        if cell:
            row, row_num = await sheet.row_values(cell.row), cell.row

        return row, row_num

    @staticmethod
    async def _get_users_sheet() -> AsyncioGspreadWorksheet:
        return await get_sheet_by_title('Юзеры')
