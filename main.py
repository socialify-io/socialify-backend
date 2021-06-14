from flask import Flask, render_template, request, jsonify
import sqlite3 as sql

app = Flask(__name__)

@app.route('/register', methods=['POST'])
def register():
    json = request.get_json(force=True) 

    if json['password'] == json['repeat_password']:
        con = sql.connect('db/users.db')
        cur = con.cursor()
        
        if (json['username'],) in cur.execute('SELECT username FROM users'):
            return '<p>Username is just owned!</p>'

        else:
            cur.execute(f'INSERT INTO users (username, password) VALUES ("{ json["username"] }", "{ json["password"] }")')
            con.commit()
            con.close()

            return '<p>Hello, Socialify!</p>'
    else:
        return '<p>Passwords is not same!</p>'

if __name__ == '__main__':
    app.run(debug=True)