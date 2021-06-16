from flask import Flask, render_template, request, jsonify
import sqlite3 as sql
import hashlib

#models
from models.errors._api_error import ApiError

from models.responses._error_response import ErrorResponse
from models.responses._response import Response

app = Flask(__name__, template_folder='templates', static_folder='static')

HTTP_METHODS = ['GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'CONNECT', 'OPTIONS', 'TRACE', 'PATCH']

@app.route('/', methods=HTTP_METHODS)
async def what_are_you_looking_for():
    return render_template('what_are_you_looking_for.html')

@app.route('/register', methods=HTTP_METHODS)
async def register():
    if request.method != 'POST':
        return render_template('what_are_you_looking_for.html')

    body = request.get_json(force=True)

    if body['password'] == body['repeat_password']:
        con = sql.connect('db/users.db')
        cur = con.cursor()
        
        if (body['username'],) in cur.execute('SELECT username FROM users'):
            error = ApiError(
                code = "InvalidUsername",
                reason = "This username is already taken."
            ).__dict__

            return jsonify(ErrorResponse(
                        errors = [error]).__dict__)

        else:
            enc_pass = hashlib.sha256(bytes(body['password'], 'utf-8')).hexdigest()

            cur.execute(f'INSERT INTO users (username, password) VALUES ("{ body["username"] }", "{ enc_pass }")')
            con.commit()
            con.close()

            return '<p>Hello, Socialify!</p>'
    else:
        error = ApiError(
            code = "InvalidRepeatPassword",
            reason = "Passwords are not same."
        ).__dict__

        return jsonify(ErrorResponse(
                    errors = [error]).__dict__)


"""
@app.route('/admin', methods=HTTP_METHODS)
def admin():
    return render_template('admin.html')
"""

if __name__ == '__main__':
    app.run(debug=True)