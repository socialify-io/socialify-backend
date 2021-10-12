from app import socketio, user_session
from flask_socketio import emit, send, join_room, leave_room
from flask import request
import json

import hashlib

# Database
from db.users_db_declarative import Device, User, DM

# Helpers
from ...helpers.get_headers import get_headers, with_fingerprint, without_fingerprint
from ...helpers.verify_authtoken import verify_authtoken
from ...helpers.RSA_helper import verify_sign

# Datatime
from datetime import datetime
import pytz

# Models
from models.errors._api_error import ApiError

from models.responses._error_response import ErrorResponse
from models.responses._response import Response

from models.errors.codes._error_codes import Error

@socketio.event
def send_dm(data):
    headers = get_headers(request, with_fingerprint)
    user_id = user_session.query(Device.userId).filter(Device.fingerprint == headers['Fingerprint']).one()[0]
    username = user_session.query(User.username).filter(User.id ==
            user_id).one()[0]

    receiver_id = data.pop('receiverId')
    message = data.pop('message')

    sids = json.loads(user_session.query(User.sids).filter(User.id == receiver_id).one()[0])
    sids.append(request.sid)

    new_dm = DM(
        receiver = receiver_id,
        sender = user_id,
        message = message,
        date = datetime.utcfromtimestamp(headers['Timestamp']).replace(tzinfo=pytz.utc)
    )

    user_session.add(new_dm)
    user_session.commit()

    emit_model = {
        'receiverId': receiver_id,
        'senderId': user_id,
        'message': message,
        'username': username,
        'date': str(datetime.utcfromtimestamp(headers['Timestamp']).replace(tzinfo=pytz.utc))
    }

    emit('send_dm', emit_model, to=sids)

@socketio.event
def fetch_last_unread_dms():
    headers = get_headers(request, with_fingerprint)
    user_id = user_session.query(Device.userId).filter(Device.fingerprint == headers['Fingerprint']).one()[0]

    dms = user_session.query(DM).filter(DM.receiver == user_id, DM.is_read == False).all()
    users_with_new_dms = []

    for dm in dms:
        if dm.sender in users_with_new_dms:
            pass
        else:
            users_with_new_dms.append(dm.sender)

    dms_json = []

    for user in users_with_new_dms:
        dm = user_session.query(DM).filter(DM.receiver == user_id, DM.sender == user).order_by(DM.id.desc()).first()
        dm_json = {
            'sender': dm.sender,
            'receiver': dm.receiver,
            'message': dm.message,
            'date': str(dm.date.replace(tzinfo=pytz.utc)),
            'isRead': dm.is_read
        }

        dms_json.append(dm_json)

    emit('fetch_dms', dms_json, to=request.sid)

