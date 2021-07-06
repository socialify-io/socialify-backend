from __main__ import app, HTTP_METHODS, route, key_session, user_session
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
        password = decrypt_private_key(body['password'], priv_key)

    except:
        error = ApiError(
            code=Error().InvalidPasswordEncryption,
            reason='Invalid password encryption.'
        ).__dict__

        return jsonify(ErrorResponse(
            errors=[error]).__dict__)

    enc_pass_sha1 = hashlib.sha1(bytes(password, 'utf-8')).hexdigest()
    enc_pass_sha256 = hashlib.sha256(bytes(enc_pass_sha1, 'utf-8')).hexdigest() 
    enc_pass_sha512 = hashlib.sha512(bytes(enc_pass_sha256, 'utf-8')).hexdigest()
    enc_pass_blake2b = hashlib.blake2b(bytes(enc_pass_sha512, 'utf-8')).hexdigest()

    usernames = user_session.query(User.username).all()
    passwords = user_session.query(User.password).all()

    if (body['username'],) in usernames and (enc_pass_blake2b,) in passwords:
        return jsonify(Response(data={}).__dict__)
    else:
        error = ApiError(
            code=Error().InvalidUsernameOrPassword,
            reason='Invalid username or password.'
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
