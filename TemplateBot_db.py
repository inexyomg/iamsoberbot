import os
import sqlite3
from datetime import datetime
from TemplateBot_const import *

def con_db(s):
    con = sqlite3.connect(os.path.join(resource_dir, db))
    cur = con.cursor()
    cur.execute(s)
    if s[:6] != 'SELECT':
        con.commit()
        con.close()
    if s[:6] == 'SELECT':
        rez = cur.fetchall()
        con.close()
        return rez

def read_bd(id, field):
    if id == 'fio':
        result = con_db(f"SELECT fio FROM IdData WHERE (fio LIKE '{' '.join(field)}%') OR (fio LIKE '{' '.join(field[::-1])}%')")
        if len(result) == 1: return result[0][0]
        return -1
    fields = ", ".join(field)
    result = con_db(f"SELECT {fields} FROM IdData WHERE id={id}")
    if len(result) == 1:
        if len(field) == 1: return result[0][0]
        return [i for i in result[0]]
    return -1

def write_bd(id, field, value):
    if type(field) == list:
        fields = ''
        for i in zip(field, value): fields += f"{i[0]}='{i[1]}', "
        fields = fields[:-2]
    if type(id) == list:
        con_db(f"UPDATE IdData SET {fields} WHERE (fio LIKE '{' '.join(id)}%') OR (fio LIKE '{' '.join(id[::-1])}%')")
    else:
        con_db(f"UPDATE IdData SET {fields} WHERE id='{id}'")

def inc_bd(id, field, value):
    con_db(f"UPDATE IdData SET {field}={field}+{value} WHERE id={id}")

def stat_bd(id,value1,value2=''):
    #Запись действия для отладки и проверки
    con_db(f'INSERT INTO StatData VALUES ("{id}","{datetime.now().date()}","{datetime.now().time().replace(microsecond=0)}","{value1}","{value2}")')