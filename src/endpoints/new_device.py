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
from ..helpers.RSA_helper import encrypt_rsa, generate_keys, decrypt_rsa

from Crypto.PublicKey import RSA
import base64
import bcrypt
import hashlib

auth_token_begin_header = '$begin-newDevice$'
auth_token_end_header = '$end-newDevice$'

@app.route(f'{route}/newDevice', methods=HTTP_METHODS)
async def new_device():
    if request.method != 'POST':
        return render_template('what_are_you_looking_for.html')

    try:
        user_agent = request.headers['User-Agent']
        os = request.headers['OS']
        timestamp = request.headers['Timestamp']
        app_version = request.headers['AppVersion']
        auth_token = bytes(request.headers['AuthToken'], 'utf-8')

    except:
        error = ApiError(
            code = Error().InvalidHeaders,
            reason = 'Some required request headers not found.'
        ).__dict__
        
        return jsonify(ErrorResponse(
                    errors = [error]).__dict__)

    auth_token_check = bytes(f'{auth_token_begin_header}.{app_version}+{os}+{user_agent}#{timestamp}#.{auth_token_end_header}', 'utf-8')

    if bcrypt.checkpw(auth_token_check, auth_token):
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
            password = bytes(decrypt_rsa(body['password'], priv_key), 'utf-8')

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

                userId = user_session.query(User.id).filter(User.username == body['username']).one()

                date = datetime.utcfromtimestamp(body['device']['timestamp']).replace(tzinfo=pytz.utc)

                new_device = Device(
                    userId=userId[0],
                    appVersion=body['device']['appVersion'],
                    os=body['device']['os'],
                    pubKey=body['device']['signPubKey'],
                    fingerprint=body['device']['fingerprint'],
                    deviceName=body['device']['deviceName'],
                    timestamp=date
                )   

                user_session.add(new_device)
                user_session.commit()

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
    else:
        error = ApiError(
            code = Error().InvalidAuthToken,
            reason = 'Your authorization token is not valid.'
        ).__dict__

        return jsonify(ErrorResponse(
                    errors = [error]).__dict__)