from app import socketio, user_session
from flask_socketio import emit
from flask import request

import hashlib

# Database
from db.users_db_declarative import Device

# Helpers
from ...helpers.get_headers import get_headers, with_fingerprint, without_fingerprint
from ...helpers.verify_authtoken import verify_authtoken
from ...helpers.RSA_helper import verify_sign

# Models
from models.errors._api_error import ApiError
from models.responses._error_response import ErrorResponse
from models.responses._response import Response
from models.errors.codes._error_codes import Error
from models._status_codes import Status

@socketio.on('connect')
def connect():
    try:
        signature = request.headers['Signature']
        headers = get_headers(request, with_fingerprint)

    except:
        error = ApiError(
            code = Error().InvalidHeaders,
            reason = 'Some required request headers not found.'
        ).__dict__

        print('Some required request headers not found.')

        emit('connect', ErrorResponse(
                        errors = [error]).__dict__)
        return

    if verify_authtoken(headers, 'connect'):
        try:
            print(headers['Fingerprint'])
            userId = user_session.query(Device.userId).filter(Device.fingerprint == headers['Fingerprint']).one()
            print('dupa')
            print(userId)
            userId = int(userId[0])

        except:
            error = ApiError(
                code = Error().InvalidFingerprint,
                reason = 'Fingerprint is not valid. Device may be deleted.'
            ).__dict__

            print('Fingerprint is not valid. Device may be deleted.')

            emit('connect', ErrorResponse(
                        errors = [error]).__dict__)
            return

        pub_key = user_session.query(Device.pubKey).filter(Device.userId == userId, Device.id == headers['DeviceId']).one()

        if verify_sign(request, pub_key, 'connect'):
            message_token_core = hashlib.sha1(bytes(
                f'{headers["Timestamp"]}.{signature}.{headers["Fingerprint"]}', 'utf-8')).hexdigest().upper()
            message_token = f'#AUTH.{message_token_core}'
            
            user_session.query(Device).filter(Device.userId == userId).filter(Device.fingerprint == headers['Fingerprint']).update(dict(messageToken=message_token))
            user_session.query(Device).filter(Device.userId == userId).filter(Device.fingerprint == headers['Fingerprint']).update(dict(status=Status().Active))

            user_session.commit()

            print("requeścik podpisany picuś glancuś 🤙")
            emit('connect', Response(data={'messageToken': message_token}).__dict__)
            return
        else: 
            error = ApiError(
                code = Error().InvalidSignature,
                reason = 'Signature is not valid.'
            ).__dict__

            print('Signature is not valid.')

            emit('connect', ErrorResponse(
                        errors = [error]).__dict__)
            return
    else:
        error = ApiError(
            code = Error().InvalidAuthToken,
            reason = 'Your authorization token is not valid.'
        ).__dict__

        print('Your authorization token is not valid.')

        emit('connect', ErrorResponse(
                        errors = [error]).__dict__)
        return
