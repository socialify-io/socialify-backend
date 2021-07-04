import sqlite3 as sql

conn = sql.connect('keys.db')

conn.execute('CREATE TABLE keys (pubKey TEXT, privKey TEXT)')

conn.close()