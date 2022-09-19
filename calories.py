from db import *
from TemplateBot_function import *


class Calories:

    def __init__(self, db_file):
        '''Инициализация'''
        self.conn = sqlite3.connect('E:\\Study\\TemplateBot\\source\\iamsober.db')
        self.cursor = self.conn.cursor()

    def count_calories(self, user_id):
        global cal_amount
        if 0 < BotDB.get_age_processed(user_id, '') <= 3:
            cal_amount = 1000
        else:
            cal_amount = 600
        return cal_amount


