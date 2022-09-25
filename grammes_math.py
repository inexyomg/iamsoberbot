from db import *
from TemplateBot_function import *


class grammes_math:

    def __init__(self, db_file):
        '''Инициализация'''
        self.conn = sqlite3.connect('E:\\Study\\TemplateBot\\source\\iamsober.db')
        self.cursor = self.conn.cursor()

    def count_s_dgrammes(self, sugar):
        global full_sugar
        full_sugar = full_sugar + sugar
        return full_sugar
