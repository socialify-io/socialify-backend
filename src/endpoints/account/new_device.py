from sys import byteorder
from app import app, HTTP_METHODS, route, key_session, user_session
from flask import render_template, request, jsonify
import os

# Database
from db.keys_db_declarative import Key
from db.users_db_declarative import User, Device

# Helpers
from ...helpers.get_headers import get_headers, with_device_id, without_device_id
from ...helpers.verify_authtoken import verify_authtoken
from ...helpers.RSA_helper import decrypt_rsa

# Crypto
from Crypto.PublicKey import RSA
import bcrypt
import base64
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.serialization import load_pem_public_key, load_pem_private_key
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes

# Datatime
from datetime import datetime
import pytz

# Models
from models.errors._api_error import ApiError
from models.responses._error_response import ErrorResponse
from models.responses._response import Response
from models.errors.codes._error_codes import Error
from models._status_codes import Status


@app.route(f'{route}/newDevice', methods=HTTP_METHODS)
async def new_device():
    if request.method != 'POST':
        return render_template('what_are_you_looking_for.html')

    try:
        headers = get_headers(request, without_device_id)

    except:
        error = ApiError(
            code = Error().InvalidHeaders,
            reason = 'Some required request headers not found.'
        ).__dict__

        return jsonify(ErrorResponse(
                    error=error).__dict__)

    if verify_authtoken(headers, "newDevice"):
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
                error=error).__dict__)

        priv_key = load_pem_private_key(bytes(priv_key, 'utf-8'), password=None)
        client_pub_key = load_pem_public_key(bytes(body['clientPubKey'], 'utf-8'))
        shared_key = priv_key.exchange(ec.ECDH(), client_pub_key)
        derived_key = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=None,
            info=None,

        ).derive(shared_key)

        decrypt_key = AESGCM(derived_key)

        nonce = [x.to_bytes(1, byteorder='big', signed=True) for x in body['nonce']]
        nonce = b''.join(nonce)
        
        try:
            password = decrypt_key.decrypt(nonce, base64.b64decode(body['password']), None)

        except:
            error = ApiError(
                code=Error().InvalidPasswordEncryption,
                reason='Invalid password encryption.'
            ).__dict__

            return jsonify(ErrorResponse(
                error=error).__dict__)

        usernames = user_session.query(User.username).all()

        if (body['username'],) in usernames:
            db_password = user_session.query(User.password).filter(User.username == body['username']).one()

            if bcrypt.checkpw(password, db_password[0]):
                key_session.query(Key).filter(Key.pub_key==pub_key_string).delete()
                key_session.commit()

                user_id = user_session.query(User.id).filter(User.username ==
                        body['username']).one()[0]

                date = datetime.utcfromtimestamp(headers['Timestamp']).replace(tzinfo=pytz.utc)

                new_device = Device(
                    userId=user_id,
                    appVersion=headers['AppVersion'],
                    os=headers['OS'],
                    pubKey=body['device']['signPubKey'],
                    deviceName=body['device']['deviceName'],
                    deviceIP=request.remote_addr,
                    timestamp=date,
                    last_active=date,
                    status=Status().Inactive
                )

                user_session.add(new_device)
                user_session.flush()
                device_id = new_device.id

                user_session.commit()

                response = Response(
                    data = {
                        "deviceId": f'{device_id}',
                        "userId": f'{user_id}'
                    }
                )

                return jsonify(response.__dict__)
            else:
                error = ApiError(
                code=Error().InvalidPassword,
                reason='Invalid password.'
            ).__dict__

            return jsonify(ErrorResponse(
                error=error).__dict__)
        else:
            error = ApiError(
                code=Error().InvalidUsername,
                reason='Invalid username.'
            ).__dict__

            return jsonify(ErrorResponse(
                error=error).__dict__)
    else:
        error = ApiError(
            code = Error().InvalidAuthToken,
            reason = 'Your authorization token is not valid.'
        ).__dict__

        return jsonify(ErrorResponse(
                    error=error).__dict__)
