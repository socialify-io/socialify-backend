from __main__ import app, HTTP_METHODS, route
from flask import Flask, render_template, request, jsonify

import sqlite3 as sql
import hashlib

#models
from models.errors._api_error import ApiError

from models.responses._error_response import ErrorResponse
from models.responses._response import Response
from models.errors.codes._error_codes import Error

# crypto
from .pass_enc import encrypt_public_key, generate_keys, decrypt_private_key

from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from base64 import b64decode, b64encode


@app.route(f'{route}/register', methods=HTTP_METHODS)
async def register():
    if request.method != 'POST':
        return render_template('what_are_you_looking_for.html')

    body = request.get_json(force=True)

    con = sql.connect('db/users.db')
    con_keys = sql.connect('db/keys.db')

    cur = con.cursor()
    cur_keys = con_keys.cursor()

    pub_key_string = body['pubKey']
    cur_keys.execute(f'SELECT privKey FROM keys WHERE pubKey="{ pub_key_string }"')
    priv_key = cur_keys.fetchone()[0]

    priv_key = RSA.importKey(priv_key)

    password = decrypt_private_key(body['password'], priv_key)
    repeat_password = decrypt_private_key(body['repeat_password'], priv_key)

    con_keys.close()

    if password == repeat_password:
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
            enc_pass = hashlib.sha256(bytes(password, 'utf-8')).hexdigest()

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