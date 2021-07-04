from __main__ import app, HTTP_METHODS, route
from flask import Flask, render_template, request, jsonify

import sqlite3 as sql
import hashlib

#models
from models.errors._api_error import ApiError

from models.responses._error_response import ErrorResponse
from models.responses._response import Response
from models.errors.codes._error_codes import Error

@app.route(f'{route}/register', methods=HTTP_METHODS)
async def register():
    if request.method != 'POST':
        return render_template('what_are_you_looking_for.html')

    body = request.get_json(force=True)

    if body['password'] == body['repeat_password']:
        con = sql.connect('db/users.db')
        cur = con.cursor()
        
        if (body['username'],) in cur.execute('SELECT username FROM users'):
            error = ApiError(
                code = Error().InvalidUsername,
                reason = "This username is already taken."
            ).__dict__

            return jsonify(ErrorResponse(
                        errors = [error]).__dict__)

        else:
            enc_pass = hashlib.sha256(bytes(body['password'], 'utf-8')).hexdigest()

            cur.execute(f'INSERT INTO users (username, password) VALUES ("{ body["username"] }", "{ enc_pass }")')
            con.commit()
            con.close()

            return jsonify(Response(data={}).__dict__)
    else:
        error = ApiError(
            code = Error().InvalidRepeatPassword,
            reason = "Passwords are not same."
        ).__dict__

        return jsonify(ErrorResponse(
                    errors = [error]).__dict__)