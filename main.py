import asyncio

from loguru import logger

from bot.runner import run_bot

logger.add('errors.log', level="ERROR", rotation='500MB')


@logger.catch(Exception)
async def main():
    await run_bot()


if __name__ == '__main__':
    asyncio.run(main())
