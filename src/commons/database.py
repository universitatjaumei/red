import sqlite3
import yaml
import os

class Database:
    def __init__(self, dbconfig):
        dbfile = os.path.join(os.path.dirname(__file__), '..', '..', dbconfig.get("db_file"))
        self.db = self.create_or_open_db(dbfile)
        self.db.row_factory = self.dict_factory

    def dict_factory(self, cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    def create_or_open_db(self, db_file):
        db_is_new = not os.path.exists(db_file)
        conn = sqlite3.connect(db_file, check_same_thread=False)
        if db_is_new:
            sql = '''create table if not exists red(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                domain TEXT UNIQUE,
                url TEXT,
                date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                active BOOL DEFAULT true);'''
            conn.execute(sql)
        return conn

    def get_redirections(self):
        cursor = self.db.cursor()
        cursor.execute ('''SELECT id, domain, url, date_added, active from red order by id desc''')
        rows = []
        for row in cursor:
            rows.append(row)
        return rows

    def get_redirection(self, id):
        cursor = self.db.cursor()
        cursor.execute ('''SELECT id, domain, url, date_added, active from red where id=?''', (id, ))
        return cursor.fetchone()

    def get_redirection_by_domain(self, domain):
        cursor = self.db.cursor()
        cursor.execute ('''SELECT id, domain, url, date_added, active from red where domain=?''', (domain, ))
        return cursor.fetchone()

    def add_redirection(self, red):
        cursor = self.db.cursor()
        self.db.execute ('''INSERT INTO red(domain, url) VALUES(?, ?)''', (red['domain'], red['url']))
        self.db.commit()
        return self.get_redirection(cursor.lastrowid)

    def del_redirection(self, id):
        self.db.execute ('''DELETE FROM red WHERE id=?''', (id, ))
        self.db.commit()

    def del_redirection_by_domain(self, domain):
        self.db.execute ('''DELETE FROM red WHERE domain=?''', (domain, ))
        self.db.commit()
