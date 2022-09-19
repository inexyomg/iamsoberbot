import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.markdown import text, bold, italic
from aiogram.types import ParseMode
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton
import asyncio
from datetime import datetime
from TemplateBot_db import *
from TemplateBot import bot, dp
from TemplateBot_const import *
import random
import time

async def botsendmes(text, id=myid, type='Мне', rm=None):
    #Отправить сообщение пользователю. На случай, если пользователь заблокировал бота - работа с исключением.
    try:
        await bot.send_message(id, text, reply_markup=rm, parse_mode="HTML")
    except Exception as e:
        stat_bd('', f'{id} {type} Бот недоступен: {e}')
    else:
        stat_bd('', f'{id} {type} Сообщение отправлено')

async def botstart():
    date = datetime.today().replace(microsecond=0)
    nd = (datetime.today() - datetime(*datestart)).days
    stat_bd('', f'{date}_{nd}')
    result = con_db(f"SELECT id FROM IdData WHERE id<>''")
    for i in result:
        id = i[0]
        await botsendmes(f"Задание", id, type='Задание', rm=None)
        stat_bd(id, f"Задание:")
        state = dp.current_state(chat=id, user=id)
        await state.reset_state()
        await state.update_data(T0=time.time())
        await asyncio.sleep(1)

async def botsendmessage():
    stat_bd('', f'{datetime.today().hour}:{datetime.today().minute}')
    nd = (datetime.today() - datetime(*datestart)).days
    if nd < 1: return
    result = con_db(f"SELECT id, fio FROM IdData WHERE id<>''")
    for i in result:
        id, fio = i
        await botsendmes(f'Здравствуйте, {" ".join(fio.split()[1:])}!\nНапоминаю о необходимости ввода ответа на задание:', id, type='Напоминание', rm=None)
        await asyncio.sleep(1)