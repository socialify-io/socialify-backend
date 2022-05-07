import sqlite3 as sql

conn = sql.connect('db/users.db')

conn.execute('''CREATE TABLE users
    (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        password TEXT NOT NULL,
        sids TEXT NOT NULL
     )''')

conn.execute('''CREATE TABLE devices
    (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        userId INTEGER NOT NULL,
        appVersion TEXT NOT NULL,
        os TEXT NOT NULL,
        pubKey TEXT NOT NULL,
        deviceName TEXT NOT NULL,
        deviceIP VARCHAR(15) NOT NULL,
        timestamp TIMESTAMP NOT NULL,
        last_active TIMESTAMP NOT NULL,
        status INTEGER NOT NULL,

        FOREIGN KEY (userId) REFERENCES users (id)
    )''')

conn.execute('''CREATE TABLE friend_requests
    (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
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
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        inviter INTEGER NOT NULL,
        invited INTEGER NOT NULL,

        FOREIGN KEY (inviter) REFERENCES users (id),
        FOREIGN KEY (invited) REFERENCES users (id)
    )''')

conn.execute('''CREATE TABLE dms
    (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        message TEXT NULL,
        sender INTEGER NOT NULL,
        receiver INTEGER NOT NULL,
        date TIMESTAMP NOT NULL,
        is_read BOOL NOT NULL DEFAULT false,

        FOREIGN KEY (sender) REFERENCES users (id),
        FOREIGN KEY (receiver) REFERENCES users (id)
    )''')

conn.execute('''CREATE TABLE rooms
    (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        is_public BOOL NOT NULL,
        password TEXT
    )''')

conn.execute('''CREATE TABLE room_roles
    (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL
    )''')

conn.execute('''INSERT INTO room_roles (id, name) VALUES (1, "owner")''')
conn.execute('''INSERT INTO room_roles (id, name) VALUES (2, "member")''')

conn.execute('''CREATE TABLE room_members
    (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        room INTEGER NOT NULL,
        user INTEGER NOT NULL,
        role INTEGER NOT NULL,

        FOREIGN KEY (role) REFERENCES room_roles (id),
        FOREIGN KEY (room) REFERENCES rooms (id),
        FOREIGN KEY (user) REFERENCES users (id)
    )''')

conn.execute('''CREATE TABLE messages
    (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        room INTEGER NOT NULL,
        sender INTEGER DEFAULT NULL,
        is_system_notification BOOL NOT NULL DEFAULT FALSE,
        message TEXT NOT NULL,
        date TIMESTAMP NOT NULL,

        FOREIGN KEY (room) REFERENCES rooms (id),
        FOREIGN KEY (sender) REFERENCES users (id)
    )''')

conn.execute('''CREATE TABLE media_types
    (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type VARCHAR(10) NOT NULL
    )''')

conn.execute('''INSERT INTO media_types (id, type) VALUES (1, "image")''')

conn.execute('''CREATE TABLE media
    (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        mediaURL TEXT NOT NULL,
        type INT NOT NULL,
        dmId INT,
        messageId INT,

        FOREIGN KEY (type) REFERENCES media_types (id),
        FOREIGN KEY (dmId) REFERENCES dms (id),
        FOREIGN KEY (messageId) REFERENCES messages (id)
    )''')

conn.close()
