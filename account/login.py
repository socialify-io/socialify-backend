from __main__ import app, HTTP_METHODS, route
from flask import Flask, render_template, request, jsonify

import sqlite3 as sql
import hashlib

#models
from models.errors._api_error import ApiError

from models.responses._error_response import ErrorResponse
from models.responses._response import Response

from models.errors.codes._error_codes import Error

#crypto
from .pass_enc import generate_keys

@app.route(f'{route}/login', methods=HTTP_METHODS)
async def login():
    if request.method != 'POST':
        return render_template('what_are_you_looking_for.html')

    body = request.get_json(force=True)

    con = sql.connect('db/users.db')
    cur = con.cursor()

    enc_pass = hashlib.sha256(bytes(body['password'], 'utf-8')).hexdigest()

    if (body['username'],) in cur.execute('SELECT username FROM users') and (enc_pass,) in cur.execute('SELECT password FROM users'):
        return jsonify(Response(data={}).__dict__)
    else:
        error = ApiError(
            code = Error().InvalidUsernameOrPassword,
            reason = "Invalid username or password."
        ).__dict__

        return jsonify(ErrorResponse(
                    errors = [error]).__dict__)

@app.route(f'{route}/getkey', methods=HTTP_METHODS)
async def getKey():
    if request.method != 'POST':
        return render_template('what_are_you_looking_for.html')

    key = generate_keys()

    pub_key = key.publickey()

    con = sql.connect('db/keys.db')
    cur = con.cursor()
    
    cur.execute(f'INSERT INTO keys (pubKey, privKey) VALUES ("{ key.exportKey() }", "{ pub_key.exportKey() }")')

    con.close()
    
    response = Response(
        data = {
            "pubKey": f'{pub_key.exportKey()}'
        }
    )

    return jsonify(response.__dict__)