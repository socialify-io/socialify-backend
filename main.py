from flask import Flask, render_template, request, jsonify
import sqlite3 as sql
import hashlib

app = Flask(__name__, template_folder='templates', static_folder='static')

HTTP_METHODS = ['GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'CONNECT', 'OPTIONS', 'TRACE', 'PATCH']

@app.route('/', methods=HTTP_METHODS)
def what_are_you_looking_for():
    return render_template('what_are_you_looking_for.html')

@app.route('/register', methods=HTTP_METHODS)
def register():
    if request.method != 'POST':
        return render_template('what_are_you_looking_for.html')

    json = request.get_json(force=True)

    if json['password'] == json['repeat_password']:
        con = sql.connect('db/users.db')
        cur = con.cursor()
        
        if (json['username'],) in cur.execute('SELECT username FROM users'):
            return '<p>Username is just owned!</p>'

        else:
            enc_pass = hashlib.sha256(bytes(json['password'], 'utf-8')).hexdigest()

            cur.execute(f'INSERT INTO users (username, password) VALUES ("{ json["username"] }", "{ enc_pass }")')
            con.commit()
            con.close()

            return '<p>Hello, Socialify!</p>'
    else:
        return '<p>Passwords is not same!</p>'

@app.route('/admin', methods=HTTP_METHODS)
def admin():
    return render_template('admin.html')

if __name__ == '__main__':
    app.run(debug=True)