from __main__ import app, HTTP_METHODS, route, session
from flask import Flask, render_template, request, jsonify
from db.keys_db_declarative import Base, Key

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
    cur = con.cursor()

    pub_key_string = body['pubKey']

    try:
        priv_key = session.query(Key).filter(Key.pub_key == pub_key_string).one()
        priv_key = priv_key.priv_key

    except TypeError:
        error = ApiError(
            code=Error().InvalidPublicRSAKey,
            reason='Invalid public RSA key.'
        ).__dict__

        return jsonify(ErrorResponse(
            errors=[error]).__dict__)

    priv_key = RSA.importKey(priv_key)

    try:
        password = decrypt_private_key(body['password'], priv_key)

    except:
        error = ApiError(
            code=Error().InvalidPasswordEncryption,
            reason='Invalid password encryption.'
        ).__dict__

        return jsonify(ErrorResponse(
            errors=[error]).__dict__)

    repeat_password = decrypt_private_key(body['repeat_password'], priv_key)

    if password == repeat_password:
        con = sql.connect('db/users.db')
        cur = con.cursor()
        
        if (body['username'],) in cur.execute('SELECT username FROM users'):
            error = ApiError(
                code = Error().InvalidUsername,
                reason = 'This username is already taken.'
            ).__dict__

            return jsonify(ErrorResponse(
                        errors = [error]).__dict__)

        else:
            enc_pass_sha1 = hashlib.sha1(bytes(password, 'utf-8')).hexdigest()
            enc_pass_sha256 = hashlib.sha256(bytes(enc_pass_sha1, 'utf-8')).hexdigest() 
            enc_pass_sha512 = hashlib.sha512(bytes(enc_pass_sha256, 'utf-8')).hexdigest()
            enc_pass_blake2b = hashlib.blake2b(bytes(enc_pass_sha512, 'utf-8')).hexdigest()

            cur.execute(f'INSERT INTO users (username, password) VALUES ("{ body["username"] }", "{ enc_pass_blake2b }")')
            con.commit()
            con.close()

            return jsonify(Response(data={}).__dict__)
    else:
        error = ApiError(
            code = Error().InvalidRepeatPassword,
            reason = 'Passwords are not same.'
        ).__dict__
        
        return jsonify(ErrorResponse(
                    errors = [error]).__dict__)