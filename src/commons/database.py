import sqlite3
import yaml
import os

class Database:
    def __init__(self):
        filename = os.path.join(os.path.dirname(__file__), '..', '..', self._get_filename())
        self.db = self.create_or_open_db(filename)
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
            print 'Creating schema'
            sql = '''create table if not exists red(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                host TEXT,
                url TEXT,
                date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                active BOOL DEFAULT true);'''
            conn.execute(sql)
        return conn

    def _get_filename(self):
        f = open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "config.yml"))
        data = yaml.safe_load(f)
        f.close()
        return data.get("database").get("filename")

    def get_redirections(self):
        cursor = self.db.cursor()
        cursor.execute ('''SELECT id, host, url, date_added, active from red''')
        rows = []
        for row in cursor:
            rows.append(row)
        return rows

    def get_redirection(self, id):
        cursor = self.db.cursor()
        cursor.execute ('''SELECT id, host, url, date_added, active from red where id=?''', (id, ))
        return cursor.fetchone()

    def add_redirection(self, red):
        cursor = self.db.cursor()
        self.db.execute ('''INSERT INTO red(host, url) VALUES(?, ?)''', (red['hostname'], red['url']))
        self.db.commit()
        return self.get_redirection(cursor.lastrowid)

    def del_redirection(self, id):
        self.db.execute ('''DELETE FROM red WHERE id=?''', (id, ))
        self.db.commit()
