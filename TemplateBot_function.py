import logging
import sqlite3

from aiogram.types.message import ContentType
from aiogram.types.message import ContentTypes
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton
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
from TemplateBot import bot, dp
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

    # --- products ---
    drinks = State()
    sweets = State()
    milks = State()
    flakes = State()
    sauces = State()

class DialogSG(StatesGroup):
    greeting = State()

markup_reply = types.ReplyKeyboardMarkup(resize_keyboard=True)
registry = DialogRegistry(dp)  # this is required to use `aiogram_dialog`

############## СТАРТ ##############

@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message, dialog_manager: DialogManager):
    if (not BotDB.user_exists(message.from_user.id)):
        BotDB.add_user(message.from_user.id, None, None)

    await bot.send_photo(message.from_user.id, types.InputFile('E:\\Study\\TemplateBot\\source\\sugar_start.jpg'),
                         caption='Привет, {0.first_name}!'.format(
                           message.from_user) + '\n\nЭтот бот поможет тебе оставаться в форме и контроллировать ежедневное потребление сахара и соли. \n\nСколько добавленных сахаров мы потребляем на самом деле? \nВыбери продукты, входящие в твоё дневное меню, и узнаем!')

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
        # await bot.send_message(message.from_user.id, 'Ваш пол: Мужчина')
    elif message.data == "btnFemale":
        BotDB.add_gender(message.from_user.id, 'Женщина', None)
        await state.update_data(gender='Женщина')
        async with state.proxy() as data:
            data['gender'] = 'Ваш пол: Женщина'
        # await bot.send_message(message.from_user.id, 'Ваш пол: Женщина')

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
    # await bot.send_message(message.from_user.id, '{0.first_name}, '.format(
    #     message.from_user) + 'Ваша суточная потребность в энергии: ' + cal_amount + ' ккал' + '\nРекомендуемое суточное количество добавленного сахара: ' + sug_amount)
    # time.sleep(0.4)
    await bot.send_photo(message.from_user.id, types.InputFile('E:\\Study\\TemplateBot\\source\\purple_calc.jpg'),
                         caption='<i>Ваша суточная потребность в энергии: </i>' + f'<i><ins>{cal_amount}</ins></i>' + '<i> ккал</i>' + '\n\n<i>Рекомендуемое суточное количество добавленного сахара: </i>' + f'<i><ins>{sug_amount}</ins></i>' + '\n\n<i>Найдите самые похожие продукты, которые сегодня употребляли, введите использованное количество и добавьте в список продуктов.</i>',
                         reply_markup=nav.btnAllProducts)


# вернуться обратно в поле всех продуктов
@dp.callback_query_handler(text='btnBack')
async def accept_all_products_back(message: types.Message):
    await accept_sugar(message)


# --------------------------------------------------------------DRINKS---------------------------------------------------------
# зайти в поле Напитки
@dp.callback_query_handler(text='btnDrinks')
async def accept_drinks(message: types.Message):
    await bot.delete_message(message.from_user.id, message.message.message_id)
    await bot.send_message(message.from_user.id, 'Выберите наиболее похожие продукты 👇',
                           reply_markup=nav.btn_DrinksProducts)


@dp.callback_query_handler(text_contains='btn_Drink_')
async def grammes_drink(message: types.CallbackQuery):
    await bot.delete_message(message.from_user.id, message.message.message_id)

    if message.data == "btn_Drink_So":
        await bot.send_message(message.from_user.id,
                               'Введите SOOO! примерное потребляемое количество в граммах.\n\n<i>Например, напитки Cola можно найти в бутылках и банках вместимостью 200, 250, 330, 500, 1000, 1500 и 2000 граммов. Один стакан напитка Cola весит примерно 200 г.</i>')
    elif message.data == "btn_Drink_Ic":
        await bot.send_message(message.from_user.id,
                               'Введите III!! примерное потребляемое количество в граммах.\n\n<i>Например, напитки Cola можно найти в бутылках и банках вместимостью 200, 250, 330, 500, 1000, 1500 и 2000 граммов. Один стакан напитка Cola весит примерно 200 г.</i>')
    elif message.data == "btn_Drink_Fr":
        await bot.send_message(message.from_user.id,
                               'Введите FR!! примерное потребляемое количество в граммах.\n\n<i>Например, напитки Cola можно найти в бутылках и банках вместимостью 200, 250, 330, 500, 1000, 1500 и 2000 граммов. Один стакан напитка Cola весит примерно 200 г.</i>')
    elif message.data == "btn_Drink_En":
        await bot.send_message(message.from_user.id,
                               'Введите En!! примерное потребляемое количество в граммах.\n\n<i>Например, напитки Cola можно найти в бутылках и банках вместимостью 200, 250, 330, 500, 1000, 1500 и 2000 граммов. Один стакан напитка Cola весит примерно 200 г.</i>')
    elif message.data == "btn_Drink_Ch":
        await bot.send_message(message.from_user.id,
                               'Введите Ch!! примерное потребляемое количество в граммах.\n\n<i>Например, напитки Cola можно найти в бутылках и банках вместимостью 200, 250, 330, 500, 1000, 1500 и 2000 граммов. Один стакан напитка Cola весит примерно 200 г.</i>')
    elif message.data == "btn_Drink_Sp":
        await bot.send_message(message.from_user.id,
                               'Введите Sp!! примерное потребляемое количество в граммах.\n\n<i>Например, напитки Cola можно найти в бутылках и банках вместимостью 200, 250, 330, 500, 1000, 1500 и 2000 граммов. Один стакан напитка Cola весит примерно 200 г.</i>')
    await OrderDialog.drinks.set()


@dp.message_handler(state=OrderDialog.drinks)
async def grammes_d_chosen(message: types.Message, state: FSMContext):
    answer = message.text
    await state.update_data(drinks=answer)
    await state.finish()
    print('hello')
    # await accept_drinks(message)
    await bot.send_message(message.from_user.id, 'Выберите DR! наиболее похожие продукты 👇',
                           reply_markup=nav.btn_DrinksProducts)


# --------------------------------------------------------------DRINKS---------------------------------------------------------
# --------------------------------------------------------------SWEETS---------------------------------------------------------
# зайти в поле Сладости
@dp.callback_query_handler(text='btnSweets')
async def accept_sweets(message: types.Message):
    await bot.delete_message(message.from_user.id, message.message.message_id)
    await bot.send_message(message.from_user.id, 'Выберите наиболее похожие продукты 👇',
                           reply_markup=nav.btn_SweetsProducts)


@dp.callback_query_handler(text_contains='btn_Sweet_')
async def grammes_sweet(message: types.CallbackQuery):
    await bot.delete_message(message.from_user.id, message.message.message_id)

    if message.data == "btn_Sweet_Su":
        await bot.send_message(message.from_user.id,
                               'Введите SOLLLOO! примерное потребляемое количество в граммах.\n\n<i>Например, напитки Cola можно найти в бутылках и банках вместимостью 200, 250, 330, 500, 1000, 1500 и 2000 граммов. Один стакан напитка Cola весит примерно 200 г.</i>')
    elif message.data == "btn_Sweet_Sw":
        await bot.send_message(message.from_user.id,
                               'Введите III!! примерное потребляемое количество в граммах.\n\n<i>Например, напитки Cola можно найти в бутылках и банках вместимостью 200, 250, 330, 500, 1000, 1500 и 2000 граммов. Один стакан напитка Cola весит примерно 200 г.</i>')
    elif message.data == "btn_Sweet_Co":
        await bot.send_message(message.from_user.id,
                               'Введите FR!! примерное потребляемое количество в граммах.\n\n<i>Например, напитки Cola можно найти в бутылках и банках вместимостью 200, 250, 330, 500, 1000, 1500 и 2000 граммов. Один стакан напитка Cola весит примерно 200 г.</i>')
    elif message.data == "btn_Sweet_Gl":
        await bot.send_message(message.from_user.id,
                               'Введите En!! примерное потребляемое количество в граммах.\n\n<i>Например, напитки Cola можно найти в бутылках и банках вместимостью 200, 250, 330, 500, 1000, 1500 и 2000 граммов. Один стакан напитка Cola весит примерно 200 г.</i>')
    elif message.data == "btn_Sweet_Ba":
        await bot.send_message(message.from_user.id,
                               'Введите Ch!! примерное потребляемое количество в граммах.\n\n<i>Например, напитки Cola можно найти в бутылках и банках вместимостью 200, 250, 330, 500, 1000, 1500 и 2000 граммов. Один стакан напитка Cola весит примерно 200 г.</i>')
    elif message.data == "btn_Sweet_Ho":
        await bot.send_message(message.from_user.id,
                               'Введите Sp!! примерное потребляемое количество в граммах.\n\n<i>Например, напитки Cola можно найти в бутылках и банках вместимостью 200, 250, 330, 500, 1000, 1500 и 2000 граммов. Один стакан напитка Cola весит примерно 200 г.</i>')
    elif message.data == "btn_Sweet_Ch":
        await bot.send_message(message.from_user.id,
                               'Введите Sp!! примерное потребляемое количество в граммах.\n\n<i>Например, напитки Cola можно найти в бутылках и банках вместимостью 200, 250, 330, 500, 1000, 1500 и 2000 граммов. Один стакан напитка Cola весит примерно 200 г.</i>')
    elif message.data == "btn_Sweet_Ja":
        await bot.send_message(message.from_user.id,
                               'Введите Sp!! примерное потребляемое количество в граммах.\n\n<i>Например, напитки Cola можно найти в бутылках и банках вместимостью 200, 250, 330, 500, 1000, 1500 и 2000 граммов. Один стакан напитка Cola весит примерно 200 г.</i>')
    elif message.data == "btn_Sweet_Ca":
        await bot.send_message(message.from_user.id,
                               'Введите Sp!! примерное потребляемое количество в граммах.\n\n<i>Например, напитки Cola можно найти в бутылках и банках вместимостью 200, 250, 330, 500, 1000, 1500 и 2000 граммов. Один стакан напитка Cola весит примерно 200 г.</i>')

    await OrderDialog.sweets.set()


@dp.message_handler(state=OrderDialog.sweets)
async def grammes_sw_chosen(message: types.Message, state: FSMContext):
    answer = message.text
    print(answer + ' г')
    await state.update_data(sweets=answer)
    await state.finish()
    print('hello')
    await bot.send_message(message.from_user.id, 'Выберите SW! наиболее похожие продукты 👇',
                           reply_markup=nav.btn_SweetsProducts)


# --------------------------------------------------------------SWEETS---------------------------------------------------------
# --------------------------------------------------------------MILKS---------------------------------------------------------
# зайти в поле Молочка
@dp.callback_query_handler(text='btnMilks')
async def accept_milks(message: types.Message):
    await bot.delete_message(message.from_user.id, message.message.message_id)
    await bot.send_message(message.from_user.id, 'Выберите наиболее похожие продукты 👇',
                           reply_markup=nav.btn_MilksProducts)


@dp.callback_query_handler(text_contains='btn_Milk_')
async def grammes_milk(message: types.CallbackQuery):
    await bot.delete_message(message.from_user.id, message.message.message_id)

    if message.data == "btn_Milk_Mi":
        await bot.send_message(message.from_user.id,
                               'Введите SOLLLOO! примерное потребляемое количество в граммах.\n\n<i>Например, напитки Cola можно найти в бутылках и банках вместимостью 200, 250, 330, 500, 1000, 1500 и 2000 граммов. Один стакан напитка Cola весит примерно 200 г.</i>')
    elif message.data == "btn_Milk_MiW":
        await bot.send_message(message.from_user.id,
                               'Введите III!! примерное потребляемое количество в граммах.\n\n<i>Например, напитки Cola можно найти в бутылках и банках вместимостью 200, 250, 330, 500, 1000, 1500 и 2000 граммов. Один стакан напитка Cola весит примерно 200 г.</i>')
    elif message.data == "btn_Milk_Ice":
        await bot.send_message(message.from_user.id,
                               'Введите FR!! примерное потребляемое количество в граммах.\n\n<i>Например, напитки Cola можно найти в бутылках и банках вместимостью 200, 250, 330, 500, 1000, 1500 и 2000 граммов. Один стакан напитка Cola весит примерно 200 г.</i>')
    elif message.data == "btn_Milk_Yo":
        await bot.send_message(message.from_user.id,
                               'Введите En!! примерное потребляемое количество в граммах.\n\n<i>Например, напитки Cola можно найти в бутылках и банках вместимостью 200, 250, 330, 500, 1000, 1500 и 2000 граммов. Один стакан напитка Cola весит примерно 200 г.</i>')
    elif message.data == "btn_Milk_YoNo":
        await bot.send_message(message.from_user.id,
                               'Введите Ch!! примерное потребляемое количество в граммах.\n\n<i>Например, напитки Cola можно найти в бутылках и банках вместимостью 200, 250, 330, 500, 1000, 1500 и 2000 граммов. Один стакан напитка Cola весит примерно 200 г.</i>')
    elif message.data == "btn_Milk_YoDr":
        await bot.send_message(message.from_user.id,
                               'Введите Sp!! примерное потребляемое количество в граммах.\n\n<i>Например, напитки Cola можно найти в бутылках и банках вместимостью 200, 250, 330, 500, 1000, 1500 и 2000 граммов. Один стакан напитка Cola весит примерно 200 г.</i>')
    elif message.data == "btn_Milk_Tv":
        await bot.send_message(message.from_user.id,
                               'Введите Sp!! примерное потребляемое количество в граммах.\n\n<i>Например, напитки Cola можно найти в бутылках и банках вместимостью 200, 250, 330, 500, 1000, 1500 и 2000 граммов. Один стакан напитка Cola весит примерно 200 г.</i>')
    elif message.data == "btn_Milk_TvCr":
        await bot.send_message(message.from_user.id,
                               'Введите Sp!! примерное потребляемое количество в граммах.\n\n<i>Например, напитки Cola можно найти в бутылках и банках вместимостью 200, 250, 330, 500, 1000, 1500 и 2000 граммов. Один стакан напитка Cola весит примерно 200 г.</i>')

    await OrderDialog.milks.set()


@dp.message_handler(state=OrderDialog.milks)
async def grammes_milk_chosen(message: types.Message, state: FSMContext):
    answer = message.text
    print(answer + ' г')
    await state.update_data(milks=answer)
    await state.finish()
    print('hello')
    await bot.send_message(message.from_user.id, 'Выберите SW! наиболее похожие продукты 👇',
                           reply_markup=nav.btn_MilksProducts)


# --------------------------------------------------------------MILKS---------------------------------------------------------
# --------------------------------------------------------------FLAKES---------------------------------------------------------
# зайти в поле Мюсли
@dp.callback_query_handler(text='btnFlakes')
async def accept_milks(message: types.Message):
    await bot.delete_message(message.from_user.id, message.message.message_id)
    await bot.send_message(message.from_user.id, 'Выберите наиболее похожие продукты 👇',
                           reply_markup=nav.btn_FlakesProducts)


@dp.callback_query_handler(text_contains='btn_Flakes_')
async def grammes_milk(message: types.CallbackQuery):
    await bot.delete_message(message.from_user.id, message.message.message_id)

    if message.data == "btn_Flakes_Ch":
        await bot.send_message(message.from_user.id,
                               'Введите SOLLLOO! примерное потребляемое количество в граммах.\n\n<i>Например, напитки Cola можно найти в бутылках и банках вместимостью 200, 250, 330, 500, 1000, 1500 и 2000 граммов. Один стакан напитка Cola весит примерно 200 г.</i>')
    elif message.data == "btn_Flakes_Br":
        await bot.send_message(message.from_user.id,
                               'Введите III!! примерное потребляемое количество в граммах.\n\n<i>Например, напитки Cola можно найти в бутылках и банках вместимостью 200, 250, 330, 500, 1000, 1500 и 2000 граммов. Один стакан напитка Cola весит примерно 200 г.</i>')
    elif message.data == "btn_Flakes_Nu":
        await bot.send_message(message.from_user.id,
                               'Введите FR!! примерное потребляемое количество в граммах.\n\n<i>Например, напитки Cola можно найти в бутылках и банках вместимостью 200, 250, 330, 500, 1000, 1500 и 2000 граммов. Один стакан напитка Cola весит примерно 200 г.</i>')
    elif message.data == "btn_Flakes_Fa":
        await bot.send_message(message.from_user.id,
                               'Введите En!! примерное потребляемое количество в граммах.\n\n<i>Например, напитки Cola можно найти в бутылках и банках вместимостью 200, 250, 330, 500, 1000, 1500 и 2000 граммов. Один стакан напитка Cola весит примерно 200 г.</i>')

    await OrderDialog.flakes.set()


@dp.message_handler(state=OrderDialog.flakes)
async def grammes_flakes_chosen(message: types.Message, state: FSMContext):
    answer = message.text
    print(answer + ' г')
    await state.update_data(flakes=answer)
    await state.finish()
    print('hello')
    await bot.send_message(message.from_user.id, 'Выберите SW! наиболее похожие продукты 👇',
                           reply_markup=nav.btn_FlakesProducts)


# --------------------------------------------------------------FLAKES---------------------------------------------------------
# --------------------------------------------------------------SAUCE---------------------------------------------------------
# зайти в поле Мюсли
@dp.callback_query_handler(text='btnSauce')
async def accept_sauces(message: types.Message):
    await bot.delete_message(message.from_user.id, message.message.message_id)
    await bot.send_message(message.from_user.id, 'Выберите наиболее похожие продукты 👇',
                           reply_markup=nav.btn_SaucesProducts)


@dp.callback_query_handler(text_contains='btn_Sauces_')
async def grammes_sauce(message: types.CallbackQuery):
    await bot.delete_message(message.from_user.id, message.message.message_id)
    await bot.send_message(message.from_user.id,
                           'Введите SOLLLOO! примерное потребляемое количество в граммах.\n\n<i>Например, напитки Cola можно найти в бутылках и банках вместимостью 200, 250, 330, 500, 1000, 1500 и 2000 граммов. Один стакан напитка Cola весит примерно 200 г.</i>')
    await OrderDialog.sauces.set()


@dp.message_handler(state=OrderDialog.sauces)
async def grammes_sauces_chosen(message: types.Message, state: FSMContext):
    answer = message.text
    print(answer + ' г')
    await state.update_data(sauces=answer)
    await state.finish()
    print('hello')
    await bot.send_message(message.from_user.id, 'Выберите SW! наиболее похожие продукты 👇',
                           reply_markup=nav.btn_SaucesProducts)


@dp.callback_query_handler(text='btnSalt')
async def accept_salt(message: types.CallbackQuery):
    await bot.answer_callback_query(callback_query_id=message.id, text="Пока недоступно", show_alert=True)


@dp.callback_query_handler(text='btnYes')
async def accept_yes(message: types.Message):
    print('Урааа')
    await bot.delete_message(message.from_user.id, message.message.message_id)
    await bot.send_message(message.from_user.id, 'Выберите, содержание чего вы хотите проверить в вашей еде? ',
                           reply_markup=nav.btnChoose)


@dp.callback_query_handler(text='btnNo')
async def accept_no(message: types.Message):
    # await bot.delete_message(message.from_user.id, message.message.message_id)
    await ready(message)


# @dp.callback_query_handler(text='btnYes')
# async def count_calories(message: types.Message):
#     if 0 < BotDB.get_age_processed(message.from_user.id) <= 3:
#         cal_amount = 1000
#     else:
#         print(500)


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

@dp.message_handler(commands=["help"], state=None)
async def cmd_help(message: types.Message,
                   start=False):  # Для отладки start поможет отличить запуск этой функции при подключении от /help
    com = ',\n'.join([f'/{i} - {botmenu[i]}' for i in botmenu]) + '.'
    s = '''Перед Вами - бот, который поможет Вам избавиться от вредных привычек
    Команды бота:'''
    await message.answer(s + '\n' + com, reply_markup=ReplyKeyboardRemove())
    if not start: stat_bd(message.from_user.id, 'Help')


@dp.message_handler(commands=["question"], state=None)
async def cmd_question(message: types.Message, state: FSMContext):
    kb = ReplyKeyboardMarkup(resize_keyboard=True).row(KeyboardButton('Отмена'))
    await message.answer(f"Какие у Вас есть вопросы? Напишите их (или напишите Отмена)", reply_markup=kb)
    stat_bd(message.from_user.id, 'Question')
    await OrderDialog.DialogQ.set()
    await state.update_data(T0=time.time())


@dp.message_handler(content_types=types.ContentTypes.TEXT, state=OrderDialog.DialogQ)
async def cmd_answer(message: types.Message, state: FSMContext):
    id = message.from_user.id
    mt = message.text
    user_answer = await state.get_data()
    if mt.capitalize() == 'Отмена' or len(mt.split(' ')) > 2:
        await message.answer(f"Спасибо за вопрос! Ответ будет отправлен Вам чуть позже",
                             reply_markup=ReplyKeyboardRemove())
        await botsendmes(f'{id}:{message.text}')
        stat_bd(id, f'Question: {message.text}', round(time.time() - user_answer['T0']))
    else:
        await message.answer(f"Вопрос отменен!", reply_markup=ReplyKeyboardRemove())
        stat_bd(id, f'QuestionCancel: {message.text}', round(time.time() - user_answer['T0']))
    await state.reset_state()


@dp.message_handler(content_types=types.ContentTypes.TEXT, state=None)
async def InputText(message: types.Message, state: FSMContext):
    id = message.from_user.id
    mt = message.text  # Проверить '"
    mt = mt.replace('"', "'")
    user_answer = await state.get_data()
    await state.update_data(T0=time.time())
    if id == myid:
        try:
            rtext = message.reply_to_message.text
            rtext = rtext.split(":")
            if len(rtext) < 2: raise Exception("")
        except:
            pass
        else:
            # Для отправки ответа на вопрос
            await bot.send_message(rtext[0], f"Отвечаю на вопрос «{':'.join(rtext[1:])}»: {mt}")
            await message.answer("Ответ отправлен!")
            stat_bd("", f"Ответ на вопрос «{':'.join(rtext[1:])}»: {mt}")
            return
    if message.get_command() is not None:
        stat_bd(id, f'Неизвестная команда: {mt}', T0)
        s = '\n'.join([f'/{i} - {botmenu[i]}' for i in botmenu])
        await message.answer(f"Неизвестная команда бота! Используйте заданные команды:\n{s}")
        return
    # Здесь будет программа для обработки текстового ввода при необходимости
    pass
