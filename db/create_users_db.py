import sqlite3 as sql

conn = sql.connect('db/users.db')

conn.execute('''CREATE TABLE users
    (
        id INTEGER PRIMARY KEY ASC,
        username TEXT NOT NULL,
        password TEXT NOT NULL,
        avatar TEXT NOT NULL,
        sids TEXT NOT NULL
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
        deviceIP VARCHAR(15) NOT NULL,
        timestamp TIMESTAMP NOT NULL,
        last_active TIMESTAMP NOT NULL,
        messageToken VARCHAR(46) NULL,
        status INTEGER NOT NULL,

        FOREIGN KEY (userId) REFERENCES users (id)
    )''')

conn.execute('''CREATE TABLE friend_requests
    (
        id INTEGER PRIMARY KEY ASC,
        receiverId INTEGER NOT NULL,
        requesterId INTEGER NOT NULL,
        requesterUsername TEXT NOT NULL,
        requestDate TIMESTAMP NOT NULL,

        FOREIGN KEY (receiverId) REFERENCES users (id),
        FOREIGN KEY (requesterId) REFERENCES users (id),
        FOREIGN KEY (requesterUsername) REFERENCES users (id)
    )''')

conn.execute('''CREATE TABLE friendships
    (
        id INTEGER PRIMARY KEY ASC,
        inviter INTEGER NOT NULL,
        invited INTEGER NOT NULL,

        FOREIGN KEY (inviter) REFERENCES users (id),
        FOREIGN KEY (invited) REFERENCES users (id)
    )''')

conn.execute('''CREATE TABLE dms
    (
        id INTEGER PRIMARY KEY ASC,
        message TEXT NOT NULL,
        sender INTEGER NOT NULL,
        receiver INTEGER NOT NULL,
        date TIMESTAMP NOT NULL,
        is_read BOOL NOT NULL DEFAULT false,

        FOREIGN KEY (sender) REFERENCES users (id),
        FOREIGN KEY (receiver) REFERENCES users (id)
    )''')

conn.close()
