from __main__ import app, HTTP_METHODS, route
from flask import Flask, render_template, request, jsonify

import operator

import sqlite3 as sql
import hashlib

# models
from models.errors._api_error import ApiError

from models.responses._error_response import ErrorResponse
from models.responses._response import Response

from models.errors.codes._error_codes import Error

# crypto
from .pass_enc import encrypt_public_key, generate_keys, decrypt_private_key

from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from base64 import b64decode, b64encode


@app.route(f'{route}/login', methods=HTTP_METHODS)
async def login():
    if request.method != 'POST':
        return render_template('what_are_you_looking_for.html')

    body = request.get_json(force=True)

    con = sql.connect('db/users.db')
    con_keys = sql.connect('db/keys.db')

    cur = con.cursor()
    cur_keys = con_keys.cursor()

    pub_key_string = body['pubKey']
    cur_keys.execute(f'SELECT privKey FROM keys WHERE pubKey="{ pub_key_string }"')
    privKey = cur_keys.fetchone()[0]

    privKey = RSA.importKey(privKey)

    password = decrypt_private_key(body['password'], privKey)

    con_keys.close()

    enc_pass = hashlib.sha256(bytes(password, 'utf-8')).hexdigest()

    if (body['username'],) in cur.execute('SELECT username FROM users') and (enc_pass,) in cur.execute('SELECT password FROM users'):
        return jsonify(Response(data={}).__dict__)
    else:
        error = ApiError(
            code=Error().InvalidUsernameOrPassword,
            reason="Invalid username or password."
        ).__dict__

        return jsonify(ErrorResponse(
            errors=[error]).__dict__)


@app.route(f'{route}/getkey', methods=HTTP_METHODS)
async def getKey():
    if request.method != 'POST':
        return render_template('what_are_you_looking_for.html')

    key = generate_keys()

    pub_key = key.publickey().exportKey().decode('utf-8')
    priv_key = key.exportKey().decode('utf-8')

    con = sql.connect('db/keys.db')
    cur = con.cursor()

    cur.execute(
        f'INSERT INTO keys (pubKey, privKey) VALUES ("{pub_key}", "{priv_key}")')
    con.commit()

    con.close()

    response = Response(
        data={
            "pubKey": f'{pub_key}'
        }
    )

    return jsonify(response.__dict__)
