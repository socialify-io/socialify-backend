import sqlite3 as sql

conn = sql.connect('db/keys.db')

conn.execute('CREATE TABLE keys (id INTEGER PRIMARY KEY ASC, pub_key TEXT NOT NULL, priv_key TEXT NOT NULL)')

conn.close()