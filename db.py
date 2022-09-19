import sqlite3


class BotDB:

    def __init__(self, db_file):
        '''Инициализация'''
        self.conn = sqlite3.connect('E:\\Study\\TemplateBot\\source\\iamsober.db')
        self.cursor = self.conn.cursor()

    def user_exists(self, user_id):
        result = self.cursor.execute('SELECT `id` FROM `users` WHERE `user_id` = ?', (user_id,))
        return bool(len(result.fetchall()))

    def get_user_id(self, user_id):
        result = self.cursor.execute('SELECT `id` FROM `users` WHERE `user_id` = ?', (user_id,))
        return result.fetchone()[0]

    def add_user(self, user_id, gender, age):
        self.cursor.execute('INSERT INTO `users` (`user_id`, `gender`, `age`) VALUES (?, ?, ?)', (user_id, gender, age))
        return self.conn.commit()

    def add_gender(self, user_id, gender, age):
        self.cursor.execute(f"UPDATE users SET gender == ?, age == ? WHERE user_id == ?", (gender, age, user_id))
        return self.conn.commit()

    def add_age(self, user_id, age):
        self.cursor.execute(f"UPDATE users SET age == ? WHERE user_id == ?", (age, user_id))
        return self.conn.commit()

    # def get_sugar(self, user_id):
    #     result = self.cursor.execute(f"SELECT s_amount FROM sugar WHERE users_id == ? AND food == ?", (user_id,))
    #     return result.fetchone()[0]

    def get_gender_processed(self, user_id):
        result = self.cursor.execute(f"SELECT gender FROM users WHERE user_id == ?", (user_id,))
        return result.fetchone()[0]

    def get_age_processed(self, user_id):
        result = self.cursor.execute(f"SELECT age FROM users WHERE user_id == ?", (user_id,))
        return result.fetchone()[0]

    def close(self):
        self.conn.close()
