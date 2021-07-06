import sqlite3 as sql

conn = sql.connect('db/users.db')

conn.execute('CREATE TABLE users (id INTEGER PRIMARY KEY ASC, username TEXT NOT NULL, password TEXT NOT NULL)')

conn.close()