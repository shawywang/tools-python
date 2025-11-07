import sqlite3
from sqlite3 import Cursor


class Db:
    def __init__(self, cursor: Cursor):
        self.cursor = cursor

    def find_mother(self):  # 通过父亲查母亲
        pass


class N:
    def __init__(self, name: str, gender: str, pai: str, father, partner, pa_name: str, marital: str):
        self.name = name  # 姓名name
        self.gender = gender  # 性别gender
        self.pai = pai  # 派

        self.father = father  # 父亲father
        self.related = ""  # 和父亲的其他关系，如收养

        self.partner = partner  # 伴侣partner，当家的人填，另一方不填
        self.pa_name = pa_name  # 若伴侣当家，出嫁者填写当家者名字
        self.marital = marital  # 婚姻：未婚、迎娶、嫁出

        self.birth_year = 0  # 生年
        self.death_year = 0  # 卒年
        self.ancs = ""  # 祖先字符串ancestor
        self.note = ""  # 备注

    def find_partner(self, p):
        if p.partner is not None:
            self.conn.cursor().execute('select * from people where name=?', (p.partner.name,))
        elif p.pa_name is not None:
            self.conn.cursor().execute('select * from people where pa_name=?', (p.name,))
        else:
            return {"id": 0}
        p = self.conn.cursor().fetchone()
        if p is not None:
            return p
        else:
            return {"id": 0}

    def find(self, name: str):
        self.conn.cursor().execute('select * from people where name=?', (name,))
        p = self.conn.cursor().fetchone()
        if p is not None:
            return p
        else:
            return {"id": 0}

    def insert(self, p, fa_id: int, pa_id: int):
        self.conn.cursor().execute(
            'SELECT * FROM people WHERE (name, gender, pai, pa_name, marital) VALUES (?, ?, ?, ?, ?)',
            (p.name, p.gender, p.pai, p.pa_name, p.marital))
        if self.conn.cursor().fetchone() is not None:
            print(f"{p.name}'已存在")
            self.conn.close()
            return False
        self.conn.cursor().execute(
            'INSERT INTO people (name, gender, pai, father, partner, pa_name, marital) VALUES (?, ?, ?, ?, ?, ?, ?)',
            (p.name, p.gender, p.pai, fa_id, pa_id, p.pa_name, p.marital))

    def add_single(self):
        self.conn = sqlite3.connect('族谱.db')  # 连接到SQLite数据库（如果数据库不存在，它将被创建）
        cursor = self.conn.cursor()
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS people
                       (
                           id
                           INTEGER
                           PRIMARY
                           KEY,
                           name
                           TEXT
                           NOT
                           NULL,
                           gender
                           TEXT
                           NOT
                           NULL,
                           pai
                           TEXT,
                           father
                           INTEGER,
                           related
                           TEXT,
                           partner
                           INTEGER,
                           pa_name
                           TEXT,
                           marital
                           TEXT
                           NOT
                           NULL,
                           birth_year
                           INTEGER,
                           death_year
                           INTEGER,
                           ancs
                           TEXT,
                           note
                           TEXT
                       )
                       ''')
        self.conn.commit()

        pa = self.find_partner(self)
        if self.father is not None:
            fa = self.find(self.father.name)
            self.insert(self, fa['id'], pa['id'])

        if self.partner is not None:
            self.insert(self, 0, pa['id'])
        self.conn.close()  # 关闭连接


if __name__ == '__main__':
    panghuaimei = N(name="庞怀美", gender="女", pai="", father=None, partner=None, pa_name="王守玺", marital="嫁出")
    panghuaimei.add_single()
