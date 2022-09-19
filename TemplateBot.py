import asyncio
from TemplateBot_message import *
from TemplateBot_const import *
import logging
import markups as nav

import aioschedule
from datetime import datetime

from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage

bot = Bot('5360559968:AAGjPC4jpNt1248H1BTC6uzUopkpWj23r14', parse_mode="HTML") #тестовый
dp = Dispatcher(bot, storage=MemoryStorage()) #обработчик
logging.basicConfig(
    #level=logging.INFO,
    filename="TemplateBot.log",
    format="%(asctime)s - %(module)s - %(levelname)s - %(funcName)s: %(lineno)d - %(message)s",
    datefmt='%H:%M:%S',
    )

async def scheduler():
    #Сообщить, что бот запустился
    print(datetime.today().replace(microsecond=0))
    await botsendmes(f'{datetime.today().replace(microsecond=0)}')
    #Если нужно регулярно выполнять какие-нибудь действия или отправлять сообщения
    aioschedule.every().day.at("09:00").do(botstart) #В 9.00
    for i in startls: aioschedule.every().day.at(f"{i}:05").do(botsendmessage) #В другое указанное в списке время

    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)

async def on_startup(x):
    asyncio.create_task(scheduler())

if __name__ == "__main__":
    from TemplateBot_function import *
    executor.start_polling(dp, skip_updates=False, on_startup=on_startup)