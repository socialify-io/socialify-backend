from app import socketio, user_session
from flask_socketio import emit
from flask import request
import json
import hashlib

# Database
from db.users_db_declarative import User, Device

# Helpers
from ...helpers.get_headers import get_headers, with_device_id, without_device_id
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
        headers = get_headers(request, with_device_id)

    except:
        error = ApiError(
            code = Error().InvalidHeaders,
            reason = 'Some required request headers not found.'
        ).__dict__

        emit('connect', ErrorResponse(
                        error = error).__dict__)
        return

    if verify_authtoken(headers, 'connect'):
        pub_key = user_session.query(Device.pubKey).filter(Device.userId == headers['UserId'], Device.id == headers['DeviceId']).one()

        if verify_sign(request, pub_key, 'connect'):
            user_session.query(Device).filter(Device.userId == headers['UserId']).filter(Device.id == headers['DeviceId']).update(dict(status=Status().Active))

            sids = json.loads(user_session.query(User.sids).filter(User.id ==
                headers['UserId']).one()[0])
            sids.append(request.sid)
            sids = json.dumps(sids)
            user_session.query(User).filter(User.id ==
                    headers['UserId']).update({'sids': sids})

            user_session.commit()

            print("CONECTED!!!!!!!")

            emit('connect', Response(data={}).__dict__)
            return
        else:
            error = ApiError(
                code = Error().InvalidSignature,
                reason = 'Signature is not valid.'
            ).__dict__

            emit('connect', ErrorResponse(
                        error = error).__dict__)
            return
    else:
        error = ApiError(
            code = Error().InvalidAuthToken,
            reason = 'Your authorization token is not valid.'
        ).__dict__

        emit('connect', ErrorResponse(
                        error = error).__dict__)
        return

