import sqlite3 as sql

conn = sql.connect('db/users.db')

conn.execute('''CREATE TABLE users 
    (
        id INTEGER PRIMARY KEY ASC, 
        username TEXT NOT NULL, 
        password TEXT NOT NULL
     )''')

conn.execute('''CREATE TABLE devices 
    (
        id INTEGER PRIMARY KEY ASC, 
        userId INTEGER NOT NULL,
        appVersion TEXT NOT NULL,
        os TEXT NOT NULL,
        pubKey TEXT NOT NULL,
        fingerprint VARCHAR(40) NOT NULL,
        deviceName TEXT NOT NULL,
        timestamp TIMESTAMP NOT NULL
     )''')

conn.close()