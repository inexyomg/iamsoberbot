import os

myid = 000#Вставить свой id

datestart = (2022,5,18,9,0) #Дата старта бота, если важна длительность работы и т.п.

botmenu = {"help":"Справочная информация по работе бота",
           "question":"Задать вопрос"}

startls = [13, 17, 21]

base_folder = os.path.dirname(os.path.abspath(__file__))
resource_dir = os.path.join(base_folder, "TemplateBot_resources")
db = 'TemplateBot_DB.db'