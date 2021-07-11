from app import app, HTTP_METHODS, route, key_session, user_session
from flask import Flask, render_template, request, jsonify
from db.users_db_declarative import UserBase, User, Device
from .RSA_helper import encrypt_public_key, generate_keys, decrypt_private_key

from Crypto.PublicKey import RSA
from base64 import b64decode, b64encode
import bcrypt
import json
import hashlib

# models
from models.errors._api_error import ApiError

from models.responses._error_response import ErrorResponse
from models.responses._response import Response

from models.errors.codes._error_codes import Error

auth_token_begin_header = '$begin-getDevices$'
auth_token_end_header = '$end-getDevices$'

@app.route(f'{route}/getDevices', methods=HTTP_METHODS)
async def get_devices():
    if request.method != 'POST':
        return render_template('what_are_you_looking_for.html')

    try:
        user_agent = request.headers['User-Agent']
        os = request.headers['OS']
        timestamp = int(request.headers['Timestamp'])
        app_version = request.headers['AppVersion']
        auth_token = request.headers['AuthToken']
        signature = request.headers['Signature']
        fingerprint = request.headers['Fingerprint']

        headers = {
            'Content-Type': request.headers['Content-Type'],
            'User-Agent': request.headers['User-Agent'],
            'OS': request.headers['OS'],
            'Timestamp': int(request.headers['Timestamp']),
            'AppVersion': request.headers['AppVersion'],
            'AuthToken': request.headers['AuthToken'],
            'Fingerprint': request.headers['Fingerprint']
        }

    except:
        error = ApiError(
            code = Error().InvalidHeaders,
            reason = 'Some required request headers not found.'
        ).__dict__
        
        return jsonify(ErrorResponse(
                    errors = [error]).__dict__)

    auth_token_check = bytes(f'{auth_token_begin_header}.{app_version}+{os}+{user_agent}#{timestamp}#.{auth_token_end_header}', 'utf-8')

    if bcrypt.checkpw(auth_token_check, bytes(auth_token, 'utf-8')):
        try:
            userId = user_session.query(Device.userId).filter(Device.fingerprint == fingerprint).one()
            userId = int(userId[0])

        except:
            error = ApiError(
                code = Error().InvalidFingerprint,
                reason = 'Fingerprint is not valid. Device may be deleted.'
            ).__dict__

            return jsonify(ErrorResponse(
                        errors = [error]).__dict__)

        priv_key = user_session.query(Device.privKey).filter(Device.userId == userId, Device.fingerprint == fingerprint).one()
        priv_key = priv_key[0]
        priv_key = RSA.importKey(priv_key)

        signature_decrypted = decrypt_private_key(signature, priv_key)

        headers_string = json.dumps(headers)
        headers_encrypted = hashlib.sha1(bytes(headers_string, 'utf-8')).hexdigest()
        
        body = request.get_json()
        if body == None:
            body = {}

        body = json.dumps(body)
        body_encrypted = hashlib.sha1(bytes(body, 'utf-8')).hexdigest()

        signature_json_check = {
            'headers': headers_encrypted,
            'body': body_encrypted,
            'timestamp': timestamp,
            'authToken': auth_token,
            'endpointUrl': f'{route}/getDevices'
        }

        print(signature_json_check)
        print(json.loads(signature_decrypted))

        if signature_json_check == json.loads(signature_decrypted):
            devices_db = user_session.query(Device.deviceName).filter(Device.userId == userId).all()
            devices = []

            for device in devices_db:
                devices.append(device[0])

            return jsonify(Response(data=devices).__dict__)

        else:
            error = ApiError(
                code = Error().InvalidSignature,
                reason = 'Signature is not valid.'
            ).__dict__

            return jsonify(ErrorResponse(
                        errors = [error]).__dict__)

    else:
        error = ApiError(
            code = Error().InvalidAuthToken,
            reason = 'Your authorization token is not valid.'
        ).__dict__

        return jsonify(ErrorResponse(
                    errors = [error]).__dict__)