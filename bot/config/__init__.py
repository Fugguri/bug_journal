from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio.utils import from_url
from pyrogram import Client

from gsheets.api import GSheetsStorage

bot = Bot('6562205443:AAHT7G9rVYxCxdMxzTZh0TqeVpghJd3rlVU',
          parse_mode=ParseMode.HTML)
_redis = from_url('redis://localhost/13')
_redis_storage = RedisStorage(_redis)
dp = Dispatcher(storage=_redis_storage)
dp.skip_updates = True
_api_id = 22539553
_api_hash = "a828e5c85b6138c57b7702fbf9ebe227"
pyro_bot = Client("my_account", _api_id, _api_hash, phone_number='79005200846')
gsheets_storage = GSheetsStorage()
