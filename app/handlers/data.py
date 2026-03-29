from aiogram import Router
from aiogram.filters import Command
import logging

from aiogram.types import InlineKeyboardButton




logger = logging.getLogger(__name__)
data = Router("data")



@data.message(Command("datos"))
    pass
