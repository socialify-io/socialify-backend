from app import socketio, user_session
from flask_socketio import emit, send, join_room, leave_room
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

@socketio.on('join')
def join(data):
    print("joined")
    join_room(data['room'])

@socketio.on('leave')
def on_leave_room(data):
    leave_room(data['room'])
