import datetime

from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import operator

from aiogram_dialog import (
    Dialog, DialogManager, DialogRegistry, Window, StartMode,
)
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button, Multiselect, Cancel, Start
from aiogram_dialog.widgets.text import Const, Format

#
# class DialogSG(StatesGroup):
#     greeting = State()
#
#
#
# async def get_data(dialog_manager: DialogManager, **kwargs):
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
# # async def name_handler(m: Message, dialog: Dialog, manager: DialogManager):
# #   manager.current_context().dialog_data["last_text"] = m.text
# #  await m.answer(f"Nice to meet you, {m.text}")
#
#
# async def on_click(c: CallbackQuery, button: Button, manager: DialogManager):
#     counter = manager.current_context().dialog_data.get("counter", 0)
#     manager.current_context().dialog_data["counter"] = counter + 1
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
# dialog = Dialog(
#     Window(
#         Const("Hello, World!"),
#         Format("Clicked: {counter}\n"),
#         Format("Stack: {stack}\n"),
#         Format("Context: {context}\n"),
#         # Format("Last text: {last_text}\n"),
#         # Format("{now}"),
#         Button(Const("Click me!"), id="btn1", on_click=on_click),
#         Start(Const("Start new stack"), id="s1",
#               mode=StartMode.NEW_STACK, state=DialogSG.greeting),
#         multi,
#         Cancel(),
#         # Inputs work only in default stack
#         # or via reply to a message with buttons
#         # MessageInput(name_handler),
#         state=DialogSG.greeting,
#         getter=get_data,
#     ),
# )

buttMenu = InlineKeyboardMarkup(row_width=2)
btnReady = InlineKeyboardButton(text='Готов(а)', callback_data="btnReady")

buttMenu.insert(btnReady)


btnOkay = InlineKeyboardMarkup(row_width=2)
btnOk = InlineKeyboardButton(text='Ок', callback_data="btnOk")

btnOkay.insert(btnOk)



# --- gender ---
btnGender = InlineKeyboardMarkup(row_width=2)
btnMale = InlineKeyboardButton(text='Мужчина', callback_data="btnMale")
btnFemale = InlineKeyboardButton(text='Женщина', callback_data="btnFemale")

btnGender.insert(btnMale)
btnGender.insert(btnFemale)

# --- accept input ---

btnAccept = InlineKeyboardMarkup(row_width=2)
btnYes = InlineKeyboardButton(text='Да', callback_data="btnYes")
btnNo = InlineKeyboardButton(text='Отмена', callback_data="btnNo")

btnAccept.insert(btnYes)
btnAccept.insert(btnNo)

# --- choose sugar or salt ---

btnChoose = InlineKeyboardMarkup(row_width=2)
btnSugar = InlineKeyboardButton(text='🍭Сахар', callback_data="btnSugar")
btnSalt = InlineKeyboardButton(text='🧂Соль', callback_data="btnSalt")
btnInfo = InlineKeyboardButton(text='💁‍♀️Информация', callback_data="btnInfo")

btnChoose.insert(btnSugar).insert(btnSalt).insert(btnInfo)

# --- cancel sugar or salt ---
btnCancel = InlineKeyboardButton(text='🙅‍♀️Отмена', callback_data="btnCancel")

# --- choose among all products ---
btnBack = InlineKeyboardButton(text='Назад ⬅', callback_data="btnBack")
btnCount = InlineKeyboardButton(text='Посчитать', callback_data="btnCount")

btnAllProducts = InlineKeyboardMarkup(row_width=2)
btnDrinks = InlineKeyboardButton(text='🥤Напитки', callback_data="btnDrinks")
btnSweets = InlineKeyboardButton(text='🍰Сладости', callback_data="btnSweets")
btnMilks = InlineKeyboardButton(text='🥛Молочные продукты', callback_data="btnMilks")
btnFlakes = InlineKeyboardButton(text='🥣Хлопья для завтрака', callback_data="btnFlakes")
btnSauce = InlineKeyboardButton(text='🥫Соусы', callback_data="btnSauce")
btnNext = InlineKeyboardButton(text='✅Далее', callback_data="btnNext")


btnAllProducts.row(btnDrinks)
btnAllProducts.row(btnSweets)
btnAllProducts.row(btnMilks)
btnAllProducts.row(btnFlakes)
btnAllProducts.row(btnSauce)
btnAllProducts.row(btnNext)
btnAllProducts.insert(btnCancel)


# --- grammes_drink_choose ---
btn_Num_DGrammes = InlineKeyboardMarkup(row_width=3)
btn200 = InlineKeyboardButton(text='200г', callback_data="btn200")
btn250 = InlineKeyboardButton(text='250г', callback_data="btn250")
btn300 = InlineKeyboardButton(text='300г', callback_data="btn300")
btn330 = InlineKeyboardButton(text='330г', callback_data="btn330")
btn500 = InlineKeyboardButton(text='500г', callback_data="btn500")
btn750 = InlineKeyboardButton(text='750г', callback_data="btn750")
btn1000 = InlineKeyboardButton(text='1000г', callback_data="btn1000")
btn1500 = InlineKeyboardButton(text='1500г', callback_data="btn1500")
btn2000 = InlineKeyboardButton(text='2000г', callback_data="btn2000")

btn_Num_DGrammes.insert(btn200).insert(btn250).insert(btn300).insert(btn330).insert(btn500).insert(btn750)
btn_Num_DGrammes.insert(btn1000).insert(btn1500).insert(btn2000)

# --- grammes_nodrink_choose ---
btn_Num_NDGrammes = InlineKeyboardMarkup(row_width=4)
btnND5 = InlineKeyboardButton(text='5г', callback_data="btnND5")
btnND10 = InlineKeyboardButton(text='10г', callback_data="btnND10")
btnND15 = InlineKeyboardButton(text='15г', callback_data="btnND15")
btnND20 = InlineKeyboardButton(text='20г', callback_data="btnND20")
btnND30 = InlineKeyboardButton(text='30г', callback_data="btnND30")
btnND40 = InlineKeyboardButton(text='40г', callback_data="btnND40")
btnND50 = InlineKeyboardButton(text='50г', callback_data="btnND50")
btnND75 = InlineKeyboardButton(text='75г', callback_data="btnND75")
btnND100 = InlineKeyboardButton(text='100г', callback_data="btnND100")
btnND150 = InlineKeyboardButton(text='150г', callback_data="btnND150")
btnND200 = InlineKeyboardButton(text='200г', callback_data="btnND200")
btnND300 = InlineKeyboardButton(text='300г', callback_data="btnND300")
btnND500 = InlineKeyboardButton(text='500г', callback_data="btnND500")



btn_Num_NDGrammes.insert(btnND5).insert(btnND10).insert(btnND15).insert(btnND20).insert(btnND30).insert(btnND40)
btn_Num_NDGrammes.insert(btnND50).insert(btnND75).insert(btnND100).insert(btnND150).insert(btnND200)
btn_Num_NDGrammes.insert(btnND300).insert(btnND500)



# --- choose among DRINK products ---

btn_DrinksProducts = InlineKeyboardMarkup(row_width=2)
btn_Soda = InlineKeyboardButton(text='🥤Газировка', callback_data="btn_Drink_So")
btn_IceTea = InlineKeyboardButton(text='🧋Холодный чай', callback_data="btn_Drink_Ic")
btn_FruitJuice = InlineKeyboardButton(text='🧃Фруктовый сок', callback_data="btn_Drink_Fr")
btn_Energy = InlineKeyboardButton(text='⚡Энергетик', callback_data="btn_Drink_En")
btn_Champagne = InlineKeyboardButton(text='🍾Игристое', callback_data="btn_Drink_Ch")
btn_Sport = InlineKeyboardButton(text='🎾Спорт. напиток', callback_data="btn_Drink_Sp")

btn_DrinksProducts.insert(btn_Soda)
btn_DrinksProducts.insert(btn_IceTea)
btn_DrinksProducts.insert(btn_FruitJuice)
btn_DrinksProducts.insert(btn_Energy)
btn_DrinksProducts.insert(btn_Champagne)
btn_DrinksProducts.insert(btn_Sport)
# btn_DrinksProducts.insert(btnCount)
btn_DrinksProducts.insert(btnBack)

# --- choose among SWEETS products ---

btn_SweetsProducts = InlineKeyboardMarkup(row_width=2)
btn_Sugar = InlineKeyboardButton(text='🍭Сахар', callback_data="btn_Sweet_Su")
btn_Sweet = InlineKeyboardButton(text='🍬Конфеты', callback_data="btn_Sweet_Sw")
btn_Cookies = InlineKeyboardButton(text='🍪Печенье', callback_data="btn_Sweet_Co")
btn_Glazed = InlineKeyboardButton(text='🥯 Сырки', callback_data="btn_Sweet_Gl")
btn_Bars = InlineKeyboardButton(text='💈Батончик', callback_data="btn_Sweet_Ba")
btn_Honey = InlineKeyboardButton(text='🍯Мёд', callback_data="btn_Sweet_Ho")
btn_Chocolate = InlineKeyboardButton(text='🍫Шоколад', callback_data="btn_Sweet_Ch")
btn_Jam = InlineKeyboardButton(text='🍥Варенье', callback_data="btn_Sweet_Ja")
btn_Cake = InlineKeyboardButton(text='🍰Кусок торта', callback_data="btn_Sweet_Ca")

btn_SweetsProducts.insert(btn_Sugar).insert(btn_Sweet).insert(btn_Cookies)
btn_SweetsProducts.insert(btn_Glazed).insert(btn_Bars).insert(btn_Honey)
btn_SweetsProducts.insert(btn_Chocolate).insert(btn_Jam).insert(btn_Cake)
btn_SweetsProducts.insert(btnBack)

# --- choose among MILK products ---

btn_MilksProducts = InlineKeyboardMarkup(row_width=2)
btn_MilksMi = InlineKeyboardButton(text='🥛Молоко', callback_data="btn_Milk_Mi")
btn_MilksMiW = InlineKeyboardButton(text='🍼Молоко с вкус. добавками', callback_data="btn_Milk_MiW")
btn_MilksIce = InlineKeyboardButton(text='🍨Мороженое', callback_data="btn_Milk_Ice")
btn_MilksYo = InlineKeyboardButton(text='🍥Йогурт', callback_data="btn_Milk_Yo")
btn_MilksYoNo = InlineKeyboardButton(text='🫗Йогурт без вкус. добавок', callback_data="btn_Milk_YoNo")
btn_MilksYoDr = InlineKeyboardButton(text='🍶Йогуртовый напиток', callback_data="btn_Milk_YoDr")
btn_MilksTv = InlineKeyboardButton(text='🥣Творог', callback_data="btn_Milk_Tv")
btn_MilksTvCr = InlineKeyboardButton(text='🍵Творожный крем', callback_data="btn_Milk_TvCr")

btn_MilksProducts.insert(btn_MilksMi).insert(btn_MilksMiW).insert(btn_MilksIce).insert(btn_MilksYo)
btn_MilksProducts.insert(btn_MilksYoNo).insert(btn_MilksYoDr).insert(btn_MilksTv).insert(btn_MilksTvCr)
btn_MilksProducts.insert(btnBack)

# --- choose among FLAKES products ---

btn_FlakesProducts = InlineKeyboardMarkup(row_width=1)
btn_Flakes_Ch = InlineKeyboardButton(text='🍛Мюсли с шоколадом', callback_data="btn_Flakes_Ch")
btn_Flakes_Br = InlineKeyboardButton(text='🧇Подслащ. хлопья для завтрака', callback_data="btn_Flakes_Br")
btn_Flakes_Nu = InlineKeyboardButton(text='🍽️Мюсли с орехами и сухофруктами', callback_data="btn_Flakes_Nu")
btn_Flakes_Fa = InlineKeyboardButton(text='🥗Каша быстрого приготовления', callback_data="btn_Flakes_Fa")

btn_FlakesProducts.insert(btn_Flakes_Ch).insert(btn_Flakes_Br).insert(btn_Flakes_Nu).insert(btn_Flakes_Fa)
btn_FlakesProducts.insert(btnBack)

# --- choose among FLAKES products ---

btn_SaucesProducts = InlineKeyboardMarkup(row_width=1)
btn_Sauces_To = InlineKeyboardButton(text='🍅Кетчуп томатный', callback_data="btn_Sauces_To")
btn_Sauces_Ks = InlineKeyboardButton(text='🥭Кисло-сладкий соус', callback_data="btn_Sauces_Ks")
btn_Sauces_Go = InlineKeyboardButton(text='🥠Сладкая горчица', callback_data="btn_Sauces_Go")
btn_Sauces_Ki = InlineKeyboardButton(text='🥫Китайский соус', callback_data="btn_Sauces_Ki")
btn_Sauces_Sc = InlineKeyboardButton(text='🌶️Соус-дип sweet chilli', callback_data="btn_Sauces_Sc")
btn_Sauces_So = InlineKeyboardButton(text='🍶Соевый соус', callback_data="btn_Sauces_So")
btn_Sauces_Br = InlineKeyboardButton(text='🍇Брусничный соус', callback_data="btn_Sauces_Br")

btn_SaucesProducts.insert(btn_Sauces_To).insert(btn_Sauces_Ks).insert(btn_Sauces_Go).insert(btn_Sauces_Ki)
btn_SaucesProducts.insert(btn_Sauces_Sc).insert(btn_Sauces_Br).insert(btn_Sauces_So).insert(btnBack)

# -------------------------------------------- previous
# btnMain = KeyboardButton('⬅ ️Главное меню')
#
# # --- main menu ---
# btnMyHabits = KeyboardButton('Мои привычки')
# btnChHabits = KeyboardButton('Выбрать привычки')
#
# btnAboutSugar = KeyboardButton('🍬 О вреде сахара')
# btnAboutSalt = KeyboardButton('🧂 О вреде соли')
# btnOther = KeyboardButton('➡️ ‍Другое')
# mainMenu = ReplyKeyboardMarkup(resize_keyboard=True).add(btnMyHabits, btnChHabits).add(btnAboutSugar, btnAboutSalt).add(
#     btnOther)
#
# # --- other menu ---
# btnInfo = KeyboardButton('💁‍♀️Информация')
# btnAsk = KeyboardButton('❔ Задать вопрос')
# otherMenu = ReplyKeyboardMarkup(resize_keyboard=True).add(btnInfo).add(btnAsk).add(btnMain)
