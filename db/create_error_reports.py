import sqlite3 as sql

conn = sql.connect('db/error_reports.db')

conn.execute('''CREATE TABLE error_reports 
    (
        id INTEGER PRIMARY KEY ASC,
        userId INTEGER NOT NULL,
        appVersion TEXT NOT NULL,
        os TEXT NOT NULL,
        deviceName TEXT NOT NULL,
        deviceIP VARCHAR(15) NOT NULL,
        timestamp TIMESTAMP NOT NULL
    )''')

conn.close()
