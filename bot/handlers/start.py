from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.keyboards.reply import get_start_keyboard
router = Router()


@router.message(Command(commands=['start']))
async def cmd_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    markup = get_start_keyboard()
    await message.answer(f'''Здравствуйте, {message.from_user.first_name}\n
/add_project - добавить проект\n
/list_projects - список проектов\n
/add_user - Добавить нового пользователя\n''', reply_markup=markup)

# /add_ticket - добавить заявку (глюк)\n
