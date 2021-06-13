from flask import Flask
import sqlite3 as sql

app = Flask(__name__)

@app.route('/register')
def register():
    conn = sql.connect('db/users.db')
    cur = conn.cursor()
    cur.execute('INSERT INTO users (username, password) VALUES ("tutaj_jest_testowe_username_kurwa", "tutaj_jest_testowe_haslo")')
    conn.commit()
    conn.close()

    return '<p>Hello, Socialify! XDDDD</p>'

if __name__ == '__main__':
    app.run(debug=True)
