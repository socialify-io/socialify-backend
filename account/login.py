from app import app, HTTP_METHODS, route, key_session, user_session
from flask import Flask, render_template, request, jsonify
from db.keys_db_declarative import KeyBase, Key
from db.users_db_declarative import UserBase, User

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
import bcrypt


@app.route(f'{route}/login', methods=HTTP_METHODS)
async def login():
    if request.method != 'POST':
        return render_template('what_are_you_looking_for.html')

    body = request.get_json(force=True)

    pub_key_string = body['pubKey']

    try:
        priv_key = key_session.query(Key).filter(Key.pub_key == pub_key_string).one()
        priv_key = priv_key.priv_key

    except:
        error = ApiError(
            code=Error().InvalidPublicRSAKey,
            reason='Invalid public RSA key.'
        ).__dict__

        return jsonify(ErrorResponse(
            errors=[error]).__dict__)
    
    priv_key = RSA.importKey(priv_key)

    try:
        password = bytes(decrypt_private_key(body['password'], priv_key), 'utf-8')

    except:
        error = ApiError(
            code=Error().InvalidPasswordEncryption,
            reason='Invalid password encryption.'
        ).__dict__

        return jsonify(ErrorResponse(
            errors=[error]).__dict__)

    usernames = user_session.query(User.username).all()

    if (body['username'],) in usernames:
        db_password = user_session.query(User.password).filter(User.username == body['username']).one()

        if bcrypt.checkpw(password, db_password[0]):
            return jsonify(Response(data={}).__dict__)
        else:
            error = ApiError(
            code=Error().InvalidPassword,
            reason='Invalid password.'
        ).__dict__

        return jsonify(ErrorResponse(
            errors=[error]).__dict__)
    else:
        error = ApiError(
            code=Error().InvalidUsername,
            reason='Invalid username.'
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

    new_key = Key(
        pub_key = pub_key,
        priv_key = priv_key
        )

    key_session.add(new_key)
    key_session.commit()

    response = Response(
        data={
            "pubKey": f'{pub_key}'
        }
    )

    return jsonify(response.__dict__)
