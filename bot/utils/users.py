from loguru import logger

from bot.config import pyro_bot


async def get_username_by_id(user_id: int) -> str:
    chat = await pyro_bot.get_chat(user_id)
    return chat.username


async def get_user_by_id(user_id: int | str) -> tuple[str, str, int | str]:
    chat = await pyro_bot.get_chat(user_id)
    return chat.first_name, chat.username, chat.id
