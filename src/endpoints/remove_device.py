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

auth_token_begin_header = '$begin-removeDevice$'
auth_token_end_header = '$end-removeDevice$'


@app.route(f'{route}/removeDevice', methods=HTTP_METHODS)
async def remove_device():
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
            code=Error().InvalidHeaders,
            reason='Some required request headers not found.'
        ).__dict__

        return jsonify(ErrorResponse(
            errors=[error]).__dict__)

    # finally:
    #     error = ApiError(
    #         code=Error.InvalidHeaders,
    #         reason='Everything works fine!'
    #     ).__dict__
    #
    #     return jsonify(ErrorResponse(
    #       errors=[error]).__dict__)


    auth_token_check = bytes(f'{auth_token_begin_header}.{app_version}+{os}+{user_agent}#{timestamp}#.{auth_token_end_header}', 'utf-8')
    if bcrypt.checkpw(auth_token_check, auth_token):
        body = request.get_json(force=True)

        fingerprints = user_session.query(Device.fingerprint).all()
        devicenames = user_session.query(Device.deviceName).all()
        if (body['device']['fingerprint'],) in fingerprints:
            if (body['device']['deviceName'],) in devicenames:
                user_session.query(Device).filter(Device.fingerprint == body['device']['fingerprint'] and Device.deviceName == body['device']['deviceName']).delete()
                user_session.commit()

                return jsonify(Response(data={}).__dict__)

            else:
                error = ApiError(
                    code=Error.InvalidRequestPayload,
                    reason='Invalid credentials.'
                ).__dict__

                return jsonify(ErrorResponse(
                    errors=[error]).__dict__)
        else:
            error = ApiError(
                code=Error.InvalidRequestPayload,
                reason='Invalid credentials.'
            ).__dict__

            return jsonify(ErrorResponse(
                errors=[error]).__dict__)
        # else:
        #     error = ApiError(
        #         code=Error().InvalidPassword,
        #         reason='Invalid password.'
        #     ).__dict__
        #
        #     return jsonify(ErrorResponse(
        #         errors=[error].__dict__)
        #     )
