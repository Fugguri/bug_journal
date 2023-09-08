from loguru import logger

from .config import bot, dp, pyro_bot
from .handlers import project, start, ticket, user


async def run_bot():
    dp.include_router(start.router)
    dp.include_router(ticket.router)
    dp.include_router(project.router)
    dp.include_router(user.router)

    logger.success('Bot has started successfully')
    await pyro_bot.start()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
