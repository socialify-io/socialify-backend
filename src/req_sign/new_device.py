from app import app, HTTP_METHODS, route, key_session, user_session
from flask import Flask, render_template, request, jsonify
from db.keys_db_declarative import KeyBase, Key
from db.users_db_declarative import UserBase, User, Device

import json
from datetime import datetime
import pytz

# models
from models.errors._api_error import ApiError

from models.responses._error_response import ErrorResponse
from models.responses._response import Response

from models.errors.codes._error_codes import Error

# crypto
from ..RSA_helper import encrypt_public_key, generate_keys, decrypt_private_key

from Crypto.PublicKey import RSA
import base64
import bcrypt
import hashlib


@app.route(f'{route}/newDevice', methods=HTTP_METHODS)
async def new_device():
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
            key_session.query(Key).filter(Key.pub_key==pub_key_string).delete()
            key_session.commit()

            sign_keys = generate_keys()

            sign_priv_key = sign_keys.exportKey().decode('utf-8')
            sign_pub_key = sign_keys.publickey().exportKey().decode('utf-8')

            userId = user_session.query(User.id).filter(User.username == body['username']).one()

            date = datetime.utcfromtimestamp(body['timestamp']).replace(tzinfo=pytz.utc)

            new_device = Device(
                userId=userId[0],
                appVersion=body['appVersion'],
                os=body['os'],
                pubKey=sign_pub_key,
                privKey=sign_priv_key,
                fingerprint=hashlib.sha1(bytes(sign_pub_key, 'utf-8')).hexdigest(),
                deviceName=body['deviceName'],
                timestamp=date
            )   

            user_session.add(new_device)
            user_session.commit()

            data = {
                "pubKey": sign_pub_key
            }

            return jsonify(Response(data=data).__dict__)
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
