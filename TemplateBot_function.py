import logging
import sqlite3

import aioschedule
import schedule as schedule
from aiogram.types.message import ContentType
from aiogram.types.message import ContentTypes
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.executor import start
from aiogram.utils.markdown import text, bold, italic
from aiogram.types import ParseMode
import time
import random
import re

from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram_dialog import (
    Dialog, DialogManager, DialogRegistry, Window, StartMode,
)
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button, Multiselect, Cancel, Start
from aiogram_dialog.widgets.text import Const, Format
import operator

import calories
import markups as nav
from TemplateBot_db import *
# from TemplateBot import bot, dp
from TemplateBot_const import *
from TemplateBot_message import *
from db import *
from calories import *

from aiogram.types import Message
from aiogram_dialog import DialogManager, StartMode

BotDB = BotDB('E:\\Study\\TemplateBot\\source\\iamsober.db')


# try:
#     conn = sqlite3.connect('E:\\Study\\TemplateBot\\source\\iamsober.db')
#     cursor = conn.cursor()
#
#     #create user_id = 1000
#     cursor.execute("INSERT OR IGNORE INTO `users` (`user_id`, `gender`, `age`) VALUES (?, ?, ?)", (1000, 'Мужчина', 20))
#
#     #count all users
#     users = cursor.execute("SELECT * FROM `users`")
#     print(users.fetchall())
#
#     #accept changes
#     conn.commit()
#
# except sqlite3.Error as error:
#     print('Error', error)

class OrderDialog(StatesGroup):
    DialogFio = State()
    DialogQ = State()
    gender = State()
    age = State()
    grammes = State()
    product_chosen = State()
    type_product = State()
    fix_grammes = State()

    # --- products ---
    drinks = State()
    sweets = State()
    milks = State()
    flakes = State()
    sauces = State()

    # --- ACTUAL products ---
    check_g = State()
    soda = State()
    ice_tea = State()


class DialogSG(StatesGroup):
    greeting = State()


API_TOKEN = '5360559968:AAGjPC4jpNt1248H1BTC6uzUopkpWj23r14'

markup_reply = types.ReplyKeyboardMarkup(resize_keyboard=True)
logging.basicConfig(level=logging.INFO)
storage = MemoryStorage()
bot = Bot(token=API_TOKEN, parse_mode="HTML")
dp = Dispatcher(bot, storage=storage)
registry = DialogRegistry(dp)  # this is required to use `aiogram_dialog`


############## СТАРТ ##############

# async def get_select_data(dialog_manager: DialogManager, **kwargs):
#     dialog_data = dialog_manager.current_context().dialog_data
#     try:
#         print(dialog_manager.current_context().widget_data['check'])
#         # print(type(dialog_manager.current_context().widget_data['check']))
#     except KeyError:
#         pass
#     return {
#         "stack": dialog_manager.current_stack(),
#         "context": dialog_manager.current_context(),
#         "now": datetime.datetime.now(),
#         "counter": dialog_data.get("counter", 0),
#         "last_text": dialog_data.get("last_text", ""),
#         "fruits": [
#             ("Apple", "Apple"),
#             ("Pear", "Pear"),
#             ("Orange", "Orange"),
#             ("Banana", "Banana"),
#         ]
#
#     }
#
#
# multi = Multiselect(
#     Format("✓ {item[0]}"),  # E.g `✓ Apple`
#     Format("{item[0]}"),
#     id="check",
#     item_id_getter=operator.itemgetter(1),
#     items="fruits",
# )
#


@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message, dialog_manager: DialogManager):
    if (not BotDB.user_exists(message.from_user.id)):
        BotDB.add_user(message.from_user.id, None, None)

    await bot.send_photo(message.from_user.id, types.InputFile('E:\\Study\\TemplateBot\\source\\sugar_start.jpg'),
                         caption='Привет, {0.first_name}!'.format(
                             message.from_user) + '\nЭтот бот поможет тебе оставаться в форме и контроллировать ежедневное потребление сахара и соли. \n\nСколько добавленных сахаров мы потребляем на самом деле? \nВыбери продукты, входящие в твоё дневное меню, и узнаем!')
    await bot.send_message(message.from_user.id, 'Выбери свой пол и укажи возраст, чтобы начать ⬇️',
                           reply_markup=nav.buttMenu)


@dp.callback_query_handler(text_contains='ready')
async def ready_go(message: types.Message):
    await bot.delete_message(message.from_user.id, message.message.message_id)
    await bot.send_message(message.from_user.id, 'ваш вес в данный момент (укажите число в кг)')


@dp.callback_query_handler(text='btnReady', state='*')
async def ready(message: types.Message):
    await bot.delete_message(message.from_user.id, message.message.message_id)
    await OrderDialog.gender.set()
    await bot.send_message(message.from_user.id, '{0.first_name}, '.format(
        message.from_user) + 'укажите ваш пол', reply_markup=nav.btnGender)


@dp.callback_query_handler(text_contains='btn', state=OrderDialog.gender)
async def genderso(message: types.CallbackQuery):
    await bot.delete_message(message.from_user.id, message.message.message_id)
    state = Dispatcher.get_current().current_state()
    if message.data == "btnMale":
        print(message.from_user.id)
        BotDB.add_gender(message.from_user.id, "Мужчина", None)
        async with state.proxy() as data:
            data['gender'] = 'Ваш пол: Мужчина'
    elif message.data == "btnFemale":
        BotDB.add_gender(message.from_user.id, 'Женщина', None)
        await state.update_data(gender='Женщина')
        async with state.proxy() as data:
            data['gender'] = 'Ваш пол: Женщина'
    await OrderDialog.next()
    await bot.send_message(message.from_user.id, 'Укажите свой возраст (числом)')


@dp.message_handler(state=OrderDialog.age)
async def get_age(message: types.Message):
    answer = message.text
    state = Dispatcher.get_current().current_state()
    if 0 < int(answer) <= 150:
        await state.update_data(age=answer)

        async with state.proxy() as data:
            data['age'] = answer
            print(data['age'])
        BotDB.add_age(message.from_user.id, answer)

        sex = BotDB.get_gender_processed(message.from_user.id)

        await bot.send_message(message.from_user.id, 'Ваш пол: ' + sex + '\nВаш возраст: ' + data['age'])
        await state.finish()
    else:
        await bot.send_message(message.from_user.id, 'Что-то не так, повторите ввод...')
    await bot.send_message(message.from_user.id, 'Указанные данные верны?', reply_markup=nav.btnAccept)


# cancel sugar or salt

@dp.callback_query_handler(text='btnCancel')
async def cancel(message: types.Message):
    await accept_yes(message)


@dp.message_handler(commands=["choose"])
async def cmd_choose(message: types.Message, dialog_manager: DialogManager):
    BotDB.clean_sug(message.from_user.id, 0)
    await bot.send_message(message.from_user.id,
                           'Выберите, содержание чего вы хотите проверить в вашей еде?',
                           reply_markup=nav.btnChoose)


@dp.callback_query_handler(text='btnNext')
async def next_sugar(message: types.CallbackQuery):
    await bot.delete_message(message.from_user.id, message.message.message_id)
    sugar_amount = BotDB.get_sugar_g(message.from_user.id)
    print(sugar_amount)
    age = BotDB.get_age_processed(message.from_user.id)
    sex = BotDB.get_gender_processed(message.from_user.id)
    global sug_amount
    if 0 < age <= 3:
        if age < 2:
            await bot.send_message(message.from_user.id,
                                   'В таком возрасте не рекомендуется есть сахар, это может быть вредно!\n\n' + f'<b>Кол-во сахара в вашей еде:</b> {round(sugar_amount, 1)} г',
                                   reply_markup=nav.btnOkay)
        else:
            sug_amount = 27
            if sugar_amount < sug_amount:
                await bot.send_message(message.from_user.id,
                                       '<b>Рекомендуемое количество добавленного сахара:</b> ' + f'{sug_amount} г\n\n' + f'<b>Кол-во сахара в вашей еде:</b> {round(sugar_amount, 1)} г' + '\n\n<i>Вы отлично справляетесь и не превышаете своей дневной нормы! Так держать!</i>',
                                       reply_markup=nav.btnOkay)
            else:
                await bot.send_message(message.from_user.id,
                                       '<b>Рекомендуемое количество добавленного сахара:</b> ' + f'{sug_amount} г\n\n' + f'<b>Кол-во сахара в вашей еде:</b> {round(sugar_amount, 1)} г' + '\n\n<i>Ваша суточная норма превышает допустимое рекомендуемое значение! Настоятельно рекомендуем <b>снизить</b> уровень потребления сахара!</i>',
                                       reply_markup=nav.btnOkay)
    elif 4 <= age <= 8:
        sug_amount = 32
        if sugar_amount < sug_amount:
            await bot.send_message(message.from_user.id,
                                   '<b>Рекомендуемое количество добавленного сахара:</b> ' + f'{sug_amount} г\n\n' + f'<b>Кол-во сахара в вашей еде:</b> {round(sugar_amount, 1)} г' + '\n\n<i>Вы отлично справляетесь и не превышаете своей дневной нормы! Так держать!</i>',
                                   reply_markup=nav.btnOkay)
        else:
            await bot.send_message(message.from_user.id,
                                   '<b>Рекомендуемое количество добавленного сахара:</b> ' + f'{sug_amount} г\n\n' + f'<b>Кол-во сахара в вашей еде:</b> {round(sugar_amount, 1)} г' + '\n\n<i>Ваша суточная норма превышает допустимое рекомендуемое значение! Настоятельно рекомендуем <b>снизить</b> уровень потребления сахара!</i>',
                                   reply_markup=nav.btnOkay)
    elif 9 <= age <= 13:
        if sex == 'Мужчина':
            sug_amount = 45
            if sugar_amount < sug_amount:
                await bot.send_message(message.from_user.id,
                                       '<b>Рекомендуемое количество добавленного сахара:</b> ' + f'{sug_amount} г\n\n' + f'<b>Кол-во сахара в вашей еде:</b> {round(sugar_amount, 1)} г' + '\n\n<i>Вы отлично справляетесь и не превышаете своей дневной нормы! Так держать!</i>',
                                       reply_markup=nav.btnOkay)
            else:
                await bot.send_message(message.from_user.id,
                                       '<b>Рекомендуемое количество добавленного сахара:</b> ' + f'{sug_amount} г\n\n' + f'<b>Кол-во сахара в вашей еде:</b> {round(sugar_amount, 1)} г' + '\n\n<i>Ваша суточная норма превышает допустимое рекомендуемое значение! Настоятельно рекомендуем <b>снизить</b> уровень потребления сахара!</i>',
                                       reply_markup=nav.btnOkay)
        else:
            sug_amount = 41
            if sugar_amount < sug_amount:
                await bot.send_message(message.from_user.id,
                                       '<b>Рекомендуемое количество добавленного сахара:</b> ' + f'{sug_amount} г\n\n' + f'<b>Кол-во сахара в вашей еде:</b> {round(sugar_amount, 1)} г' + '\n\n<i>Вы отлично справляетесь и не превышаете своей дневной нормы! Так держать!</i>',
                                       reply_markup=nav.btnOkay)
            else:
                await bot.send_message(message.from_user.id,
                                       '<b>Рекомендуемое количество добавленного сахара:</b> ' + f'{sug_amount} г\n\n' + f'<b>Кол-во сахара в вашей еде:</b> {round(sugar_amount, 1)} г' + '\n\n<i>Ваша суточная норма превышает допустимое рекомендуемое значение! Настоятельно рекомендуем <b>снизить</b> уровень потребления сахара!</i>',
                                       reply_markup=nav.btnOkay)
    elif 14 <= age <= 18:
        if sex == 'Мужчина':
            sug_amount = 69
            if sugar_amount < sug_amount:
                await bot.send_message(message.from_user.id,
                                       '<b>Рекомендуемое количество добавленного сахара:</b> ' + f'{sug_amount} г\n\n' + f'<b>Кол-во сахара в вашей еде:</b> {round(sugar_amount, 1)} г' + '\n\n<i>Вы отлично справляетесь и не превышаете своей дневной нормы! Так держать!</i>',
                                       reply_markup=nav.btnOkay)
            else:
                await bot.send_message(message.from_user.id,
                                       '<b>Рекомендуемое количество добавленного сахара:</b> ' + f'{sug_amount} г\n\n' + f'<b>Кол-во сахара в вашей еде:</b> {round(sugar_amount, 1)} г' + '\n\n<i>Ваша суточная норма превышает допустимое рекомендуемое значение! Настоятельно рекомендуем <b>снизить</b> уровень потребления сахара!</i>',
                                       reply_markup=nav.btnOkay)
        else:
            sug_amount = 45
            if sugar_amount < sug_amount:
                await bot.send_message(message.from_user.id,
                                       '<b>Рекомендуемое количество добавленного сахара:</b> ' + f'{sug_amount} г\n\n' + f'<b>Кол-во сахара в вашей еде:</b> {round(sugar_amount, 1)} г' + '\n\n<i>Вы отлично справляетесь и не превышаете своей дневной нормы! Так держать!</i>',
                                       reply_markup=nav.btnOkay)
            else:
                await bot.send_message(message.from_user.id,
                                       '<b>Рекомендуемое количество добавленного сахара:</b> ' + f'{sug_amount} г\n\n' + f'<b>Кол-во сахара в вашей еде:</b> {round(sugar_amount, 1)} г' + '\n\n<i>Ваша суточная норма превышает допустимое рекомендуемое значение! Настоятельно рекомендуем <b>снизить</b> уровень потребления сахара!</i>',
                                       reply_markup=nav.btnOkay)
    elif 19 <= age <= 30:
        if sex == 'Мужчина':
            sug_amount = 61
            if sugar_amount < sug_amount:
                await bot.send_message(message.from_user.id,
                                       '<b>Рекомендуемое количество добавленного сахара:</b> ' + f'{sug_amount} г\n\n' + f'<b>Кол-во сахара в вашей еде:</b> {round(sugar_amount, 1)} г' + '\n\n<i>Вы отлично справляетесь и не превышаете своей дневной нормы! Так держать!</i>',
                                       reply_markup=nav.btnOkay)
            else:
                await bot.send_message(message.from_user.id,
                                       '<b>Рекомендуемое количество добавленного сахара:</b> ' + f'{sug_amount} г\n\n' + f'<b>Кол-во сахара в вашей еде:</b> {round(sugar_amount, 1)} г' + '\n\n<i>Ваша суточная норма превышает допустимое рекомендуемое значение! Настоятельно рекомендуем <b>снизить</b> уровень потребления сахара!</i>',
                                       reply_markup=nav.btnOkay)
        else:
            sug_amount = 49
            if sugar_amount < sug_amount:
                await bot.send_message(message.from_user.id,
                                       '<b>Рекомендуемое количество добавленного сахара:</b> ' + f'{sug_amount} г\n\n' + f'<b>Кол-во сахара в вашей еде:</b> {round(sugar_amount, 1)} г' + '\n\n<i>Вы отлично справляетесь и не превышаете своей дневной нормы! Так держать!</i>',
                                       reply_markup=nav.btnOkay)
            else:
                await bot.send_message(message.from_user.id,
                                       '<b>Рекомендуемое количество добавленного сахара:</b> ' + f'{sug_amount} г\n\n' + f'<b>Кол-во сахара в вашей еде:</b> {round(sugar_amount, 1)} г' + '\n\n<i>Ваша суточная норма превышает допустимое рекомендуемое значение! Настоятельно рекомендуем <b>снизить</b> уровень потребления сахара!</i>',
                                       reply_markup=nav.btnOkay)
    elif 31 <= age <= 50:
        if sex == 'Мужчина':
            sug_amount = 58
            if sugar_amount < sug_amount:
                await bot.send_message(message.from_user.id,
                                       '<b>Рекомендуемое количество добавленного сахара:</b> ' + f'{sug_amount} г\n\n' + f'<b>Кол-во сахара в вашей еде:</b> {round(sugar_amount, 1)} г' + '\n\n<i>Вы отлично справляетесь и не превышаете своей дневной нормы! Так держать!</i>',
                                       reply_markup=nav.btnOkay)
            else:
                await bot.send_message(message.from_user.id,
                                       '<b>Рекомендуемое количество добавленного сахара:</b> ' + f'{sug_amount} г\n\n' + f'<b>Кол-во сахара в вашей еде:</b> {round(sugar_amount, 1)} г' + '\n\n<i>Ваша суточная норма превышает допустимое рекомендуемое значение! Настоятельно рекомендуем <b>снизить</b> уровень потребления сахара!</i>',
                                       reply_markup=nav.btnOkay)
        else:
            sug_amount = 45
            if sugar_amount < sug_amount:
                await bot.send_message(message.from_user.id,
                                       '<b>Рекомендуемое количество добавленного сахара:</b> ' + f'{sug_amount} г\n\n' + f'<b>Кол-во сахара в вашей еде:</b> {round(sugar_amount)} г' + '\n\n<i>Вы отлично справляетесь и не превышаете своей дневной нормы! Так держать!</i>',
                                       reply_markup=nav.btnOkay)
            else:
                await bot.send_message(message.from_user.id,
                                       '<b>Рекомендуемое количество добавленного сахара:</b> ' + f'{sug_amount} г\n\n' + f'<b>Кол-во сахара в вашей еде:</b> {round(sugar_amount)} г' + '\n\n<i>Ваша суточная норма превышает допустимое рекомендуемое значение! Настоятельно рекомендуем <b>снизить</b> уровень потребления сахара!</i>',
                                       reply_markup=nav.btnOkay)
    elif age >= 51:
        if sex == 'Мужчина':
            sug_amount = 58
            if sugar_amount < sug_amount:
                await bot.send_message(message.from_user.id,
                                       '<b>Рекомендуемое количество добавленного сахара:</b> ' + f'{sug_amount} г\n\n' + f'<b>Кол-во сахара в вашей еде:</b> {round(sugar_amount)} г' + '\n\n<i>Вы отлично справляетесь и не превышаете своей дневной нормы! Так держать!</i>',
                                       reply_markup=nav.btnOkay)
            else:
                await bot.send_message(message.from_user.id,
                                       '<b>Рекомендуемое количество добавленного сахара:</b> ' + f'{sug_amount} г\n\n' + f'<b>Кол-во сахара в вашей еде:</b> {round(sugar_amount)} г' + '\n\n<i>Ваша суточная норма превышает допустимое рекомендуемое значение! Настоятельно рекомендуем <b>снизить</b> уровень потребления сахара!</i>',
                                       reply_markup=nav.btnOkay)
        else:
            sug_amount = 45
            if sugar_amount < sug_amount:
                await bot.send_message(message.from_user.id,
                                       '<b>Рекомендуемое количество добавленного сахара:</b> ' + f'{sug_amount} г\n\n' + f'<b>Кол-во сахара в вашей еде:</b> {round(sugar_amount)} г' + '\n\n<i>Вы отлично справляетесь и не превышаете своей дневной нормы! Так держать!</i>',
                                       reply_markup=nav.btnOkay)
            else:
                await bot.send_message(message.from_user.id,
                                       '<b>Рекомендуемое количество добавленного сахара:</b> ' + f'{sug_amount} г\n\n' + f'<b>Кол-во сахара в вашей еде:</b> {round(sugar_amount)} г' + '\n\n<i>Ваша суточная норма превышает допустимое рекомендуемое значение! Настоятельно рекомендуем <b>снизить</b> уровень потребления сахара!</i>',
                                       reply_markup=nav.btnOkay)


@dp.callback_query_handler(text='btnCount')
async def count_sugar(message: types.CallbackQuery):
    await bot.delete_message(message.from_user.id, message.message.message_id)
    sugar_amount = BotDB.get_sugar_g(message.from_user.id)
    print(sugar_amount)
    await bot.send_message(message.from_user.id,
                           f'Текущее суточное потребление добавленных сахаров составляет приблизительно: {round(sugar_amount, 1)} г',
                           reply_markup=nav.btnOkay)


@dp.callback_query_handler(text='btnOk')
async def ok(message: types.CallbackQuery):
    await bot.delete_message(message.from_user.id, message.message.message_id)
    BotDB.clean_sug(message.from_user.id, 0)
    await bot.send_message(message.from_user.id,
                           'Выберите, содержание чего вы хотите проверить в вашей еде?',
                           reply_markup=nav.btnChoose)


@dp.callback_query_handler(text='btnInfo')
async def information(message: types.CallbackQuery):
    await bot.delete_message(message.from_user.id, message.message.message_id)
    await bot.send_message(message.from_user.id,
                           'Калькулятор определяет примерное количество сахаров (в том числе добавленных сахаров) и соли в еде, а также сравнивает их с нормой ежедневного использования вашей возрастной группы.',
                           reply_markup=nav.btnChoose)


@dp.callback_query_handler(text='btnSugar')
async def accept_sugar(message: types.Message):
    await bot.delete_message(message.from_user.id, message.message.message_id)
    global cal_amount, sug_amount
    age = BotDB.get_age_processed(message.from_user.id)
    sex = BotDB.get_gender_processed(message.from_user.id)
    if 0 < age <= 3:
        if age < 2:
            cal_amount = '1000'
            sug_amount = 'не стоит в таком возрасте'
        else:
            cal_amount = '1000'
            sug_amount = '27 г'
    elif 4 <= age <= 8:
        cal_amount = '1400-1600'
        sug_amount = '32 г'
    elif 9 <= age <= 13:
        if sex == 'Мужчина':
            cal_amount = '1800-2200'
            sug_amount = '45 г'
        else:
            cal_amount = '1600-2000'
            sug_amount = '41 г'
    elif 14 <= age <= 18:
        if sex == 'Мужчина':
            cal_amount = '2400-2800'
            sug_amount = '69 г'
        else:
            cal_amount = '2000'
            sug_amount = '45 г'
    elif 19 <= age <= 30:
        if sex == 'Мужчина':
            cal_amount = '2600-2800'
            sug_amount = '61 г'
        else:
            cal_amount = '2000-2200'
            sug_amount = '49 г'
    elif 31 <= age <= 50:
        if sex == 'Мужчина':
            cal_amount = '2400-2600'
            sug_amount = '58 г'
        else:
            cal_amount = '2000'
            sug_amount = '45 г'
    elif age >= 51:
        if sex == 'Мужчина':
            cal_amount = '2200-2400'
            sug_amount = '58 г'
        else:
            cal_amount = '1800'
            sug_amount = '45 г'
    sugar_amount = BotDB.get_sugar_g(message.from_user.id)
    print(sugar_amount)
    await bot.send_photo(message.from_user.id, types.InputFile('E:\\Study\\TemplateBot\\source\\purple_calc.jpg'),
                         caption='<b>Суточная потребность в энергии:</b> ' + f'\n<i>{cal_amount} ккал</i>' + '\n<b>Суточная потребность в сахаре:</b> ' + f'\n<i>{sug_amount}</i>' + f'\n\n<b>Кол-во сахара в вашей еде:</b> {round(sugar_amount, 1)} г',
                         reply_markup=nav.btnAllProducts)


# вернуться обратно в поле всех продуктов
@dp.callback_query_handler(text='btnBack')
async def accept_all_products_back(message: types.Message):
    await accept_sugar(message)


# --------------------------------------------------------------OTHER---------------------------------------------------------
# --------------------------------------------------------------DRINKS---------------------------------------------------------
# зайти в поле Напитки
@dp.callback_query_handler(text='btnDrinks')
async def accept_drinks(message: types.Message):
    await bot.delete_message(message.from_user.id, message.message.message_id)
    await bot.send_message(message.from_user.id,
                           'Выберите похожие продукты 👇\n\n' + f'<b>Кол-во сахара в вашей еде:</b> {round(BotDB.get_sugar_g(message.from_user.id), 1)} г',
                           reply_markup=nav.btn_DrinksProducts)


@dp.callback_query_handler(text_contains='btn_Drink_')
async def grammes_drink(message: types.CallbackQuery, state: FSMContext):
    await bot.delete_message(message.from_user.id, message.message.message_id)
    await state.update_data(type_product='drinks')
    if message.data == "btn_Drink_So":
        await bot.send_message(message.from_user.id,
                               'Введите примерное потребляемое количество в граммах.\n\n<i>Например, напитки '
                               'Cola можно найти в бутылках и банках вместимостью 200, 250, 330, 500, 1000, '
                               '1500 и 2000 граммов. Один стакан напитка Cola весит примерно 200 г.</i>',
                               reply_markup=nav.btn_Num_DGrammes)
        await state.update_data(product_chosen='soda')
    elif message.data == "btn_Drink_Ic":
        await bot.send_message(message.from_user.id,
                               'Введите примерное потребляемое количество в граммах.\n\n<i>В продаже холодный чай можно найти в основном в бутылках по 250, 500 и 1500 граммов. Один стакан холодного чая весит примерно 200 г.</i>',
                               reply_markup=nav.btn_Num_DGrammes)
        await state.update_data(product_chosen='ice_tea')
    elif message.data == "btn_Drink_Fr":
        await bot.send_message(message.from_user.id,
                               'Введите примерное потребляемое количество в граммах.\n\n<i>Соки продаются в основном в пакетах по 1000 граммов. Стакан сока весит примерно 200 г.</i>',
                               reply_markup=nav.btn_Num_DGrammes)
        await state.update_data(product_chosen='fruit_juice')
    elif message.data == "btn_Drink_En":
        await bot.send_message(message.from_user.id,
                               'Введите примерное потребляемое количество в граммах.\n\n<i>Энергетические напитки продаются в основном в бутылках по 330 и 500 граммов. Стакан энергетического напитка весит примерно 200 г.</i>',
                               reply_markup=nav.btn_Num_DGrammes)
        await state.update_data(product_chosen='energy')
    elif message.data == "btn_Drink_Ch":
        await bot.send_message(message.from_user.id,
                               'Введите примерное потребляемое количество в граммах.\n\n<i>Игристые напитки продаются в бутылках по 750 граммов. Стандартный станкан игристого напитка весит примерно 200 г.</i>',
                               reply_markup=nav.btn_Num_DGrammes)
        await state.update_data(product_chosen='champagne')
    elif message.data == "btn_Drink_Sp":
        await bot.send_message(message.from_user.id,
                               'Введите примерное потребляемое количество в граммах.\n\n<i>Спортивные напитки продаются в основном в бутылках и банках по 750 и 1500 граммов. Стакан спортивного напитка весит примерно 200 г.</i>',
                               reply_markup=nav.btn_Num_DGrammes)
        await state.update_data(product_chosen='sport')


# --------------------------------------------------------------DRINKS---------------------------------------------------------
# --------------------------------------------------------------SWEETS---------------------------------------------------------
# зайти в поле Сладости
@dp.callback_query_handler(text='btnSweets')
async def accept_sweets(message: types.Message):
    await bot.delete_message(message.from_user.id, message.message.message_id)
    await bot.send_message(message.from_user.id,
                           'Выберите похожие продукты 👇\n\n' + f'<b>Кол-во сахара в вашей еде:</b> {round(BotDB.get_sugar_g(message.from_user.id), 1)} г',
                           reply_markup=nav.btn_SweetsProducts)


@dp.callback_query_handler(text_contains='btn_Sweet_')
async def grammes_sweet(message: types.CallbackQuery, state: FSMContext):
    await bot.delete_message(message.from_user.id, message.message.message_id)
    await state.update_data(type_product='sweets')
    if message.data == "btn_Sweet_Su":
        await bot.send_message(message.from_user.id,
                               'Введите примерное потребляемое количество в граммах.\n\n<i>Полная чайная ложка сахара весит примерно 5 г, столовая ложка – 15 г.</i>',
                               reply_markup=nav.btn_Num_NDGrammes)
        await state.update_data(product_chosen='sugar')
    elif message.data == "btn_Sweet_Sw":
        await bot.send_message(message.from_user.id,
                               'Введите примерное потребляемое количество в граммах.\n\n<i>Одна конфета весит в среднем 5 г.</i>',
                               reply_markup=nav.btn_Num_NDGrammes)
        await state.update_data(product_chosen='sweets')
    elif message.data == "btn_Sweet_Co":
        await bot.send_message(message.from_user.id,
                               'Введите примерное потребляемое количество в граммах.\n\n<i>Одно печенье весит в среднем 10 г.</i>',
                               reply_markup=nav.btn_Num_NDGrammes)
        await state.update_data(product_chosen='cookies')
    elif message.data == "btn_Sweet_Gl":
        await bot.send_message(message.from_user.id,
                               'Введите примерное потребляемое количество в граммах.\n\n<i>Имеющиеся в продаже сырки весят в среднем около 40 г.</i>',
                               reply_markup=nav.btn_Num_NDGrammes)
        await state.update_data(product_chosen='glazed')
    elif message.data == "btn_Sweet_Ba":
        await bot.send_message(message.from_user.id,
                               'Введите примерное потребляемое количество в граммах.\n\n<i>Батончики обычно весят 30 или 50 г.</i>',
                               reply_markup=nav.btn_Num_NDGrammes)
        await state.update_data(product_chosen='bars')
    elif message.data == "btn_Sweet_Ho":
        await bot.send_message(message.from_user.id,
                               'Введите примерное потребляемое количество в граммах.\n\n<i>Чайная ложка меда весит примерно 10 г, столовая ложка – 20 г.</i>',
                               reply_markup=nav.btn_Num_NDGrammes)
        await state.update_data(product_chosen='honey')
    elif message.data == "btn_Sweet_Ch":
        await bot.send_message(message.from_user.id,
                               'Введите примерное потребляемое количество в граммах.\n\n<i>В продаже имеется в основном шоколадная плитка массой 20, 100, 200 и 300 граммов. Один квадратик шоколада весит примерно 5 г.</i>',
                               reply_markup=nav.btn_Num_NDGrammes)
        await state.update_data(product_chosen='chocolate')
    elif message.data == "btn_Sweet_Ja":
        await bot.send_message(message.from_user.id,
                               'Введите примерное потребляемое количество в граммах.\n\n<i>Чайная ложка варенья весит примерно 10 г, столовая ложка – 20 г.</i>',
                               reply_markup=nav.btn_Num_NDGrammes)
        await state.update_data(product_chosen='jam')
    elif message.data == "btn_Sweet_Ca":
        await bot.send_message(message.from_user.id,
                               'Введите примерное потребляемое количество в граммах.\n\n<i>Средний кусок торта весит примерно 100 г.</i>',
                               reply_markup=nav.btn_Num_NDGrammes)
        await state.update_data(product_chosen='cake')


# --------------------------------------------------------------SWEETS---------------------------------------------------------
# --------------------------------------------------------------MILKS---------------------------------------------------------
# зайти в поле Молочка
@dp.callback_query_handler(text='btnMilks')
async def accept_milks(message: types.Message):
    await bot.delete_message(message.from_user.id, message.message.message_id)
    await bot.send_message(message.from_user.id,
                           'Выберите похожие продукты 👇\n\n' + f'<b>Кол-во сахара в вашей еде:</b> {round(BotDB.get_sugar_g(message.from_user.id), 1)} г',
                           reply_markup=nav.btn_MilksProducts)


@dp.callback_query_handler(text_contains='btn_Milk_')
async def grammes_milk(message: types.CallbackQuery, state: FSMContext):
    await bot.delete_message(message.from_user.id, message.message.message_id)
    await state.update_data(type_product='milks')
    if message.data == "btn_Milk_Mi":
        await bot.send_message(message.from_user.id,
                               'Введите примерное потребляемое количество в граммах.\n\n<i>Стакан молока весит примерно 200 г.',
                               reply_markup=nav.btn_Num_DGrammes)
        await state.update_data(product_chosen='milk')
    elif message.data == "btn_Milk_MiW":
        await bot.send_message(message.from_user.id,
                               'Введите примерное потребляемое количество в граммах.\n\n<i>Размер упаковки по преимуществу 250 г.',
                               reply_markup=nav.btn_Num_DGrammes)
        await state.update_data(product_chosen='milkw')
    elif message.data == "btn_Milk_Ice":
        await bot.send_message(message.from_user.id,
                               'Введите примерное потребляемое количество в граммах.\n\n<i>Одно небольшое мороженое на палочке весит примерно 50 г.</i>',
                               reply_markup=nav.btn_Num_NDGrammes)
        await state.update_data(product_chosen='icecream')
    elif message.data == "btn_Milk_Yo":
        await bot.send_message(message.from_user.id,
                               'Введите примерное потребляемое количество в граммах.\n\n<i>Йогурт продается в основном в стаканчиках по 100, 150, 200 и 300 граммов. Чайная ложка йогурта весит примерно 5 г, столовая ложка – 15 г.</i>',
                               reply_markup=nav.btn_Num_NDGrammes)
        await state.update_data(product_chosen='yogurt')
    elif message.data == "btn_Milk_YoNo":
        await bot.send_message(message.from_user.id,
                               'Введите примерное потребляемое количество в граммах.\n\n<i>Йогурт продается в основном в стаканчиках по 100, 150, 200 и 300 граммов. Чайная ложка йогурта весит примерно 5 г, столовая ложка – 15 г.</i>',
                               reply_markup=nav.btn_Num_NDGrammes)
        await state.update_data(product_chosen='yogurtw')
    elif message.data == "btn_Milk_YoDr":
        await bot.send_message(message.from_user.id,
                               'Введите примерное потребляемое количество в граммах.\n\n<i>В продаже имеются в основном питьевые йогурты в бутылках и пакетах по 300, 330 и 1000 граммов. Стакан питьевого йогурта весит примерно 200 г.</i>',
                               reply_markup=nav.btn_Num_DGrammes)
        await state.update_data(product_chosen='yogurt_drink')
    elif message.data == "btn_Milk_Tv":
        await bot.send_message(message.from_user.id,
                               'Введите примерное потребляемое количество в граммах.\n\n<i>Зернистый творог продается в основном по 100, 150, 200, 300, 500 граммов. Чайная ложка с горкой зернистого творога весит примерно 15 г, столовая ложка с горкой – примерно 40 г</i>',
                               reply_markup=nav.btn_Num_NDGrammes)
        await state.update_data(product_chosen='curd')
    elif message.data == "btn_Milk_TvCr":
        await bot.send_message(message.from_user.id,
                               'Введите примерное потребляемое количество в граммах.\n\n<i>Творожный крем продается в основном в стаканчиках по 100, 150 и 300 граммов. Одна чайная ложка с горкой творожного крема весит примерно 20 г, столовая ложка с горкой – примерно 40 г.</i>',
                               reply_markup=nav.btn_Num_NDGrammes)
        await state.update_data(product_chosen='curd_cream')


# --------------------------------------------------------------MILKS---------------------------------------------------------
# --------------------------------------------------------------FLAKES---------------------------------------------------------
# зайти в поле Мюсли
@dp.callback_query_handler(text='btnFlakes')
async def accept_flakes(message: types.Message):
    await bot.delete_message(message.from_user.id, message.message.message_id)
    await bot.send_message(message.from_user.id,
                           'Выберите похожие продукты 👇\n\n' + f'<b>Кол-во сахара в вашей еде:</b> {round(BotDB.get_sugar_g(message.from_user.id), 1)} г',
                           reply_markup=nav.btn_FlakesProducts)


@dp.callback_query_handler(text_contains='btn_Flakes_')
async def grammes_flakes(message: types.CallbackQuery, state: FSMContext):
    await bot.delete_message(message.from_user.id, message.message.message_id)
    await state.update_data(type_product='flakes')
    if message.data == "btn_Flakes_Ch":
        await bot.send_message(message.from_user.id,
                               'Введите примерное потребляемое количество в граммах.\n\n<i>Мюсли продаются как правило в пачках по 300–500 граммов. 100мл хлопьев весит примерно 40 г.</i>',
                               reply_markup=nav.btn_Num_NDGrammes)
        await state.update_data(product_chosen='ch_flakes')
    elif message.data == "btn_Flakes_Br":
        await bot.send_message(message.from_user.id,
                               'Введите примерное потребляемое количество в граммах.\n\n<i>Мюсли продаются как правило в пачках по 300–500 граммов. 100мл хлопьев весит примерно 40 г.</i>',
                               reply_markup=nav.btn_Num_NDGrammes)
        await state.update_data(product_chosen='br_flakes')
    elif message.data == "btn_Flakes_Nu":
        await bot.send_message(message.from_user.id,
                               'Введите примерное потребляемое количество в граммах.\n\n<i>Мюсли продаются как правило в пачках по 300–500 граммов. 100мл хлопьев весит примерно 40 г.</i>',
                               reply_markup=nav.btn_Num_NDGrammes)
        await state.update_data(product_chosen='nu_flakes')
    elif message.data == "btn_Flakes_Fa":
        await bot.send_message(message.from_user.id,
                               'Введите примерное потребляемое количество в граммах.\n\n<i>Пакет каши быстрого приготовления обычно содержит примерно 45 г сухого сырья для каши.</i>',
                               reply_markup=nav.btn_Num_NDGrammes)
        await state.update_data(product_chosen='fa_flakes')


# --------------------------------------------------------------FLAKES---------------------------------------------------------
# --------------------------------------------------------------SAUCE---------------------------------------------------------
# зайти в поле Мюсли
@dp.callback_query_handler(text='btnSauce')
async def accept_sauces(message: types.Message):
    await bot.delete_message(message.from_user.id, message.message.message_id)
    await bot.send_message(message.from_user.id,
                           'Выберите похожие продукты 👇\n\n' + f'<b>Кол-во сахара в вашей еде:</b> {round(BotDB.get_sugar_g(message.from_user.id), 1)} г',
                           reply_markup=nav.btn_SaucesProducts)


@dp.callback_query_handler(text_contains='btn_Sauces_')
async def grammes_sauce(message: types.CallbackQuery, state: FSMContext):
    await bot.delete_message(message.from_user.id, message.message.message_id)
    await state.update_data(type_product='sauces')
    if message.data == "btn_Sauces_To":
        await bot.send_message(message.from_user.id,
                               'Введите примерное потребляемое количество в граммах.\n\n<i>Чайная ложка кетчупа весит примерно 10 г, столовая ложка с горкой – около 30 г.</i>',
                               reply_markup=nav.btn_Num_NDGrammes)
        await state.update_data(product_chosen='tomate')
    elif message.data == "btn_Sauces_Ks":
        await bot.send_message(message.from_user.id,
                               'Введите примерное потребляемое количество в граммах.\n\n<i>Чайная ложка кислосладкого соуса весит примерно 10 г, столовая ложка с горкой – около 30 г.',
                               reply_markup=nav.btn_Num_NDGrammes)
        await state.update_data(product_chosen='ks')
    elif message.data == "btn_Sauces_Go":
        await bot.send_message(message.from_user.id,
                               'Введите примерное потребляемое количество в граммах.\n\n<i>Чайная ложка горчицы весит примерно 10 г, столовая ложка – 30 г.</i>',
                               reply_markup=nav.btn_Num_NDGrammes)
        await state.update_data(product_chosen='go')
    elif message.data == "btn_Sauces_Ki":
        await bot.send_message(message.from_user.id,
                               'Введите примерное потребляемое количество в граммах.\n\n<i>Столовая ложка соуса Uncle Bens или китайского соуса Spilva весит примерно 15 г.</i>',
                               reply_markup=nav.btn_Num_NDGrammes)
        await state.update_data(product_chosen='china')
    elif message.data == "btn_Sauces_Sc":
        await bot.send_message(message.from_user.id,
                               'Введите примерное потребляемое количество в граммах.\n\n<i>Чайная ложка соуса-дип весит примерно 10 г, столовая ложка – 20 г.</i>',
                               reply_markup=nav.btn_Num_NDGrammes)
        await state.update_data(product_chosen='sc')
    elif message.data == "btn_Sauces_So":
        await bot.send_message(message.from_user.id,
                               'Введите примерное потребляемое количество в граммах.\n\n<i>Чайная ложка соевого соуса весит примерно 5 г, столовая ложка – около 15 г.</i>',
                               reply_markup=nav.btn_Num_NDGrammes)
        await state.update_data(product_chosen='so')
    elif message.data == "btn_Sauces_Br":
        await bot.send_message(message.from_user.id,
                               'Введите примерное потребляемое количество в граммах.\n\n<i>Чайная ложка брусничного соуса весит примерно 10 г, столовая ложка с горкой – около 30 г.</i>',
                               reply_markup=nav.btn_Num_NDGrammes)
        await state.update_data(product_chosen='br')


# --------------------------------------------------------------SAUCE---------------------------------------------------------
# --------------------------------------------------------------OTHER---------------------------------------------------------

@dp.callback_query_handler(text='btnSalt')
async def accept_salt(message: types.CallbackQuery):
    await bot.answer_callback_query(callback_query_id=message.id, text="Пока недоступно", show_alert=True)


@dp.callback_query_handler(text='btnYes')
async def accept_yes(message: types.Message):
    print('Урааа')
    await bot.delete_message(message.from_user.id, message.message.message_id)
    await bot.send_message(message.from_user.id,
                           'Выберите, содержание какого продукта вы хотите проверить в вашей еде?',
                           reply_markup=nav.btnChoose)
    await BotDB.clean_sug(message.from_user.id, 0)


@dp.callback_query_handler(text='btnNo')
async def accept_no(message: types.Message):
    # await bot.delete_message(message.from_user.id, message.message.message_id)
    await ready(message)


@dp.callback_query_handler()
async def discover_grammes(message: types.CallbackQuery, state: FSMContext):
    if message.data == 'btn200':
        await state.update_data(fix_grammes='200')
        await grammes_soda(message, state)
    elif message.data == 'btn250':
        await state.update_data(fix_grammes='250')
        await grammes_soda(message, state)
    elif message.data == 'btn300':
        await state.update_data(fix_grammes='300')
        await grammes_soda(message, state)
    elif message.data == 'btn330':
        await state.update_data(fix_grammes='330')
        await grammes_soda(message, state)
    elif message.data == 'btn500':
        await state.update_data(fix_grammes='500')
        await grammes_soda(message, state)
    elif message.data == 'btn750':
        await state.update_data(fix_grammes='750')
        await grammes_soda(message, state)
    elif message.data == 'btn1000':
        await state.update_data(fix_grammes='1000')
        await grammes_soda(message, state)
    elif message.data == 'btn1500':
        await state.update_data(fix_grammes='1500')
        await grammes_soda(message, state)
    elif message.data == 'btn2000':
        await state.update_data(fix_grammes='2000')
        await grammes_soda(message, state)
    elif message.data == 'btnND5':
        await state.update_data(fix_grammes='5')
        await grammes_soda_nd(message, state)
    elif message.data == 'btnND10':
        await state.update_data(fix_grammes='10')
        await grammes_soda_nd(message, state)
    elif message.data == 'btnND15':
        await state.update_data(fix_grammes='15')
        await grammes_soda_nd(message, state)
    elif message.data == 'btnND20':
        await state.update_data(fix_grammes='20')
        await grammes_soda_nd(message, state)
    elif message.data == 'btnND30':
        await state.update_data(fix_grammes='30')
        await grammes_soda_nd(message, state)
    elif message.data == 'btnND40':
        await state.update_data(fix_grammes='40')
        await grammes_soda_nd(message, state)
    elif message.data == 'btnND50':
        await state.update_data(fix_grammes='50')
        await grammes_soda_nd(message, state)
    elif message.data == 'btnND75':
        await state.update_data(fix_grammes='75')
        await grammes_soda_nd(message, state)
    elif message.data == 'btnND100':
        await state.update_data(fix_grammes='100')
        await grammes_soda_nd(message, state)
    elif message.data == 'btnND150':
        await state.update_data(fix_grammes='150')
        await grammes_soda_nd(message, state)
    elif message.data == 'btnND200':
        await state.update_data(fix_grammes='200')
        await grammes_soda_nd(message, state)
    elif message.data == 'btnND300':
        await state.update_data(fix_grammes='300')
        await grammes_soda_nd(message, state)
    elif message.data == 'btnND500':
        await state.update_data(fix_grammes='500')
        await grammes_soda_nd(message, state)


# ------ DIFFRENT INPUT -------
@dp.callback_query_handler()
async def grammes_soda(message: types.CallbackQuery, state: FSMContext):
    await bot.delete_message(message.from_user.id, message.message.message_id)
    fix_grammes = await state.get_data("fix_grammes")
    answer = fix_grammes["fix_grammes"]
    print(await state.get_data("product_chosen"))
    product_chosen = await state.get_data("product_chosen")
    type_product = await state.get_data("type_product")

    if type_product['type_product'] == 'drinks':

        if product_chosen['product_chosen'] == 'soda':
            BotDB.add_sugar_g(message.from_user.id, float(answer) * 0.109)
        elif product_chosen['product_chosen'] == 'ice_tea':
            BotDB.add_sugar_g(message.from_user.id, float(answer) * 0.079)
        elif product_chosen['product_chosen'] == 'fruit_juice':
            BotDB.add_sugar_g(message.from_user.id, float(answer) * 0.091)
        elif product_chosen['product_chosen'] == 'energy':
            BotDB.add_sugar_g(message.from_user.id, float(answer) * 0.126)
        elif product_chosen['product_chosen'] == 'champagne':
            BotDB.add_sugar_g(message.from_user.id, float(answer) * 0.076)
        elif product_chosen['product_chosen'] == 'sport':
            BotDB.add_sugar_g(message.from_user.id, float(answer) * 0.078)
        await bot.send_message(message.from_user.id,
                               'Выберите похожие продукты 👇\n\n' + f'<b>Кол-во сахара в вашей еде:</b> {round(BotDB.get_sugar_g(message.from_user.id), 1)} г',
                               reply_markup=nav.btn_DrinksProducts)
    elif type_product['type_product'] == 'milks':

        if product_chosen['product_chosen'] == 'milk':
            BotDB.add_sugar_g(message.from_user.id, float(answer) * 0)
        elif product_chosen['product_chosen'] == 'milkw':
            BotDB.add_sugar_g(message.from_user.id, float(answer) * 0.079)
        elif product_chosen['product_chosen'] == 'yogurt_drink':
            BotDB.add_sugar_g(message.from_user.id, float(answer) * 0.079)
        await bot.send_message(message.from_user.id,
                               'Выберите похожие продукты 👇\n\n' + f'<b>Кол-во сахара в вашей еде:</b> {round(BotDB.get_sugar_g(message.from_user.id), 1)} г',
                               reply_markup=nav.btn_MilksProducts)


@dp.callback_query_handler()
async def grammes_soda_nd(message: types.CallbackQuery, state: FSMContext):
    await bot.delete_message(message.from_user.id, message.message.message_id)
    fix_grammes = await state.get_data("fix_grammes")
    answer = fix_grammes["fix_grammes"]
    print(await state.get_data("product_chosen"))
    product_chosen = await state.get_data("product_chosen")
    type_product = await state.get_data("type_product")

    if type_product['type_product'] == 'sweets':

        if product_chosen['product_chosen'] == 'sugar':
            BotDB.add_sugar_g(message.from_user.id, float(answer) * 1)
        elif product_chosen['product_chosen'] == 'sweets':
            BotDB.add_sugar_g(message.from_user.id, float(answer) * 0.61)
        elif product_chosen['product_chosen'] == 'cookies':
            BotDB.add_sugar_g(message.from_user.id, float(answer) * 0.021)
        elif product_chosen['product_chosen'] == 'glazed':
            BotDB.add_sugar_g(message.from_user.id, float(answer) * 0.234)
        elif product_chosen['product_chosen'] == 'bars':
            BotDB.add_sugar_g(message.from_user.id, float(answer) * 0.281)
        elif product_chosen['product_chosen'] == 'honey':
            BotDB.add_sugar_g(message.from_user.id, float(answer) * 0.791)
        elif product_chosen['product_chosen'] == 'chocolate':
            BotDB.add_sugar_g(message.from_user.id, float(answer) * 0.41)
        elif product_chosen['product_chosen'] == 'jam':
            BotDB.add_sugar_g(message.from_user.id, float(answer) * 0.456)
        elif product_chosen['product_chosen'] == 'cake':
            BotDB.add_sugar_g(message.from_user.id, float(answer) * 0.2)
        await bot.send_message(message.from_user.id,
                               'Выберите похожие продукты 👇\n\n' + f'<b>Кол-во сахара в вашей еде:</b> {round(BotDB.get_sugar_g(message.from_user.id), 1)} г',
                               reply_markup=nav.btn_SweetsProducts)
    elif type_product['type_product'] == 'milks':

        if product_chosen['product_chosen'] == 'icecream':
            BotDB.add_sugar_g(message.from_user.id, float(answer) * 0.12)
        elif product_chosen['product_chosen'] == 'yogurt':
            BotDB.add_sugar_g(message.from_user.id, float(answer) * 0.107)
        elif product_chosen['product_chosen'] == 'yogurtw':
            BotDB.add_sugar_g(message.from_user.id, float(answer) * 0)
        elif product_chosen['product_chosen'] == 'curd':
            BotDB.add_sugar_g(message.from_user.id, float(answer) * 0.04)
        elif product_chosen['product_chosen'] == 'curd_cream':
            BotDB.add_sugar_g(message.from_user.id, float(answer) * 0.126)
        await bot.send_message(message.from_user.id,
                               'Выберите похожие продукты 👇\n\n' + f'<b>Кол-во сахара в вашей еде:</b> {round(BotDB.get_sugar_g(message.from_user.id), 1)} г',
                               reply_markup=nav.btn_MilksProducts)
    elif type_product['type_product'] == 'flakes':

        if product_chosen['product_chosen'] == 'ch_flakes':
            BotDB.add_sugar_g(message.from_user.id, float(answer) * 0.228)
        elif product_chosen['product_chosen'] == 'br_flakes':
            BotDB.add_sugar_g(message.from_user.id, float(answer) * 0.365)
        elif product_chosen['product_chosen'] == 'nu_flakes':
            BotDB.add_sugar_g(message.from_user.id, float(answer) * 0.081)
        elif product_chosen['product_chosen'] == 'fa_flakes':
            BotDB.add_sugar_g(message.from_user.id, float(answer) * 0.276)
        await bot.send_message(message.from_user.id,
                               'Выберите похожие продукты 👇\n\n' + f'<b>Кол-во сахара в вашей еде:</b> {round(BotDB.get_sugar_g(message.from_user.id), 1)} г',
                               reply_markup=nav.btn_FlakesProducts)
    elif type_product['type_product'] == 'sauces':
        if product_chosen['product_chosen'] == 'tomate':
            BotDB.add_sugar_g(message.from_user.id, float(answer) * 0.17)
        elif product_chosen['product_chosen'] == 'ks':
            BotDB.add_sugar_g(message.from_user.id, float(answer) * 0.19)
        elif product_chosen['product_chosen'] == 'go':
            BotDB.add_sugar_g(message.from_user.id, float(answer) * 0.009)
        elif product_chosen['product_chosen'] == 'china':
            BotDB.add_sugar_g(message.from_user.id, float(answer) * 0.135)
        elif product_chosen['product_chosen'] == 'sc':
            BotDB.add_sugar_g(message.from_user.id, float(answer) * 0.37)
        elif product_chosen['product_chosen'] == 'so':
            BotDB.add_sugar_g(message.from_user.id, float(answer) * 0.004)
        elif product_chosen['product_chosen'] == 'br':
            BotDB.add_sugar_g(message.from_user.id, float(answer) * 0.04)
        await bot.send_message(message.from_user.id,
                               'Выберите похожие продукты 👇\n\n' + f'<b>Кол-во сахара в вашей еде:</b> {round(BotDB.get_sugar_g(message.from_user.id), 1)} г',
                               reply_markup=nav.btn_SaucesProducts)


@dp.message_handler()
async def bot_message(message: types.Message):
    if message.text == 'Мои привычки':
        await bot.send_message(message.from_user.id,
                               '<b> Мои привычки </b>')

    elif message.text == 'Готов(а)':
        await bot.send_message(message.from_user.id,
                               '<b> Мои </b>')
    elif message.text == 'Выбрать привычки':
        await bot.send_message(message.from_user.id,
                               '<b> Выбрать привычки </b>')
    elif message.text == '🍬 О вреде сахара':
        await bot.send_message(message.from_user.id,
                               '<b> О вреде сахара: </b> \n\nИзбыточное количество сахара может привести к развитию диабета, ожирению и другим проблемам в организме. Тростниковый и свекольный сахар по калорийности одинаковые, но по степени очистки и производству лучше отдать предпочтение тростниковому. Злоупотреблять им, впрочем, также не стоит.')

    elif message.text == '🧂 О вреде соли':
        await bot.send_message(message.from_user.id,
                               '<b> О вреде соли: </b> \n\nПри многократного превышения дневной нормы употребления соли она начинает накапливаться в организме. Это приводит к превышению нормального содержания натрия и хлора в тканях, формируются отеки, повышается артериальное давление. Это сопровождается спазмом сосудов, в том числе и в головном мозге.')

    elif message.text == '💁‍♀️Информация':
        await bot.send_message(message.from_user.id,
                               '<b> 💁‍♀️Информация </b> \n\nПеред Вами бот, который поможет Вам избавиться от вредных привычек. Выбирай те привычки, которыми бы ты хотел обладать.')


    elif message.text == '⬅ ️Главное меню':
        await bot.send_message(message.from_user.id, '⬅ ️Главное меню',
                               reply_markup=nav.mainMenu)
    elif message.text == '➡️ ‍Другое':
        await bot.send_message(message.from_user.id, '➡ ️‍Другое',
                               reply_markup=nav.otherMenu)

    elif message.text == 'Назад ⬅':
        await bot.send_message(message.from_user.id, '⬅ ️Главное меню',
                               reply_markup=nav.btnAllProducts)


    else:
        await message.reply('Что-то я Вас не понимаю ;(')

    # id = message.from_user.id
    # rd = read_bd(id,['fio'])
    # #Проверяем, подключен ли пользователь
    # if rd != -1:
    #     #Если подключен
    #     await message.answer(f'Здравствуйте, {" ".join(rd.split(" ")[1:])}!')
    #     stat_bd(id, 'start2')
    #     return
    #
    # button1 = KeyboardButton(f'{message.from_user.last_name} {message.from_user.first_name}')
    # button2 = KeyboardButton('Отмена')
    # kb = ReplyKeyboardMarkup(resize_keyboard=True)
    # kb.row(button1, button2)
    #
    #
    # await message.answer(f'Здравствуйте, {message.from_user.last_name} {message.from_user.first_name}! \nДля подключения бота, Вам нужно ввести/подтвердить Фамилию Имя.\n\nВведите или подтвердите свою Фамилию и Имя (*{message.from_user.last_name} {message.from_user.first_name}*). Для отмены подключения напишите/выберите "Отмена".', reply_markup=kb, parse_mode="Markdown")
    # await OrderDialog.DialogFio.set()
    # stat_bd(id, 'start')


# @dp.message_handler(content_types=types.ContentTypes.TEXT, state=OrderDialog.DialogFio)
# async def DialogFio_set(message: types.Message, state: FSMContext):
#     id = message.from_user.id
#     mt = message.text
#     if mt == 'Отмена':
#         stat_bd(id, 'start fio Отмена')
#         await state.reset_state()
#         await message.answer('Подключение бота отменено!', reply_markup=ReplyKeyboardRemove())
#         return
#     if len(mt.split()) >= 2:
#         f = mt.split()[0].capitalize()
#         i = mt.split()[1].capitalize()
#     else:
#         f = mt.capitalize()
#         i = ''
#     rd = read_bd('fio',[f,i])
#     if rd == -1:
#         button1 = KeyboardButton(f'{message.from_user.last_name} {message.from_user.first_name}')
#         button2 = KeyboardButton('Отмена')
#         kb = ReplyKeyboardMarkup(resize_keyboard=True)  # one_time_keyboard=True
#         kb.row(button1, button2)
#         await message.answer('К сожалению, Вы не являетесь участником курса и поэтому не можете использовать бота! Или же Фамилия Имя введены с ошибками. Повторите ввод или введите/выберите "Отмена".', reply_markup=kb)
#         stat_bd(id, 'start fio: Отклонение')
#         return
#     stat_bd(id, 'start fio')
#     write_bd([f,i], ['id'], [id])
#     await cmd_help(message, True)
#     #Формирование меню бота
#     lm = [types.BotCommand(i, botmenu[i]) for i in botmenu]
#     await bot.set_my_commands(lm)
#     await state.reset_state()


#
# @dp.message_handler(commands=["question"], state=None)
# async def cmd_question(message: types.Message, state: FSMContext):
#     kb = ReplyKeyboardMarkup(resize_keyboard=True).row(KeyboardButton('Отмена'))
#     await message.answer(f"Какие у Вас есть вопросы? Напишите их (или напишите Отмена)", reply_markup=kb)
#     stat_bd(message.from_user.id, 'Question')
#     await OrderDialog.DialogQ.set()
#     await state.update_data(T0=time.time())
#
# @dp.message_handler(content_types=types.ContentTypes.TEXT, state=OrderDialog.DialogQ)
# async def cmd_answer(message: types.Message, state: FSMContext):
#     id = message.from_user.id
#     mt = message.text
#     user_answer = await state.get_data()
#     if mt.capitalize() == 'Отмена' or len(mt.split(' ')) > 2:
#         await message.answer(f"Спасибо за вопрос! Ответ будет отправлен Вам чуть позже",
#                              reply_markup=ReplyKeyboardRemove())
#         await botsendmes(f'{id}:{message.text}')
#         stat_bd(id, f'Question: {message.text}', round(time.time() - user_answer['T0']))
#     else:
#         await message.answer(f"Вопрос отменен!", reply_markup=ReplyKeyboardRemove())
#         stat_bd(id, f'QuestionCancel: {message.text}', round(time.time() - user_answer['T0']))
#     await state.reset_state()


# @dp.message_handler(content_types=types.ContentTypes.TEXT, state=None)
# async def InputText(message: types.Message, state: FSMContext):
#     id = message.from_user.id
#     mt = message.text  # Проверить '"
#     mt = mt.replace('"', "'")
#     user_answer = await state.get_data()
#     await state.update_data(T0=time.time())
#     if id == myid:
#         try:
#             rtext = message.reply_to_message.text
#             rtext = rtext.split(":")
#             if len(rtext) < 2: raise Exception("")
#         except:
#             pass
#         else:
#             # Для отправки ответа на вопрос
#             await bot.send_message(rtext[0], f"Отвечаю на вопрос «{':'.join(rtext[1:])}»: {mt}")
#             await message.answer("Ответ отправлен!")
#             stat_bd("", f"Ответ на вопрос «{':'.join(rtext[1:])}»: {mt}")
#             return
#     if message.get_command() is not None:
#         stat_bd(id, f'Неизвестная команда: {mt}', T0)
#         s = '\n'.join([f'/{i} - {botmenu[i]}' for i in botmenu])
#         await message.answer(f"Неизвестная команда бота! Используйте заданные команды:\n{s}")
#         return
#     # Здесь будет программа для обработки текстового ввода при необходимости
#     pass
#

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=False)
