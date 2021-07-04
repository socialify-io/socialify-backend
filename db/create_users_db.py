import sqlite3 as sql

conn = sql.connect('users.db')

conn.execute('CREATE TABLE users (username TEXT, password TEXT)')

conn.close()