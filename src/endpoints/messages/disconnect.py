from app import socketio, user_session
from flask_socketio import emit
from flask import request

import hashlib

# Database
from db.users_db_declarative import Device

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

@socketio.on('disconnect')
def disconnect():
    headers = get_headers(request, with_device_id)

    user_session.query(Device).filter(Device.userId == headers['UserId']).filter(Device.id == headers['DeviceId']).update(dict(status=Status().Inactive))

    user_session.commit()
