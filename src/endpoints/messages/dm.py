from app import socketio, user_session
from flask_socketio import emit, send, join_room, leave_room
from flask import request
import json

import hashlib

# Database
from db.users_db_declarative import Device, User, DM

# Helpers
from ...helpers.get_headers import get_headers, with_device_id, without_device_id
from ...helpers.verify_authtoken import verify_authtoken
from ...helpers.RSA_helper import verify_sign
from ...helpers.get_user_id import get_user_id

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
    headers = get_headers(request, with_device_id)
    user_id = headers["UserId"]
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
        date = datetime.utcnow().replace(microsecond=0)
    )

    user_session.add(new_dm)
    user_session.commit()

    emit_model = {
        'id': new_dm.id,
        'receiverId': receiver_id,
        'senderId': user_id,
        'message': message,
        'username': username,
        'date': str(new_dm.date.isoformat()+'Z')
    }

    emit('send_dm', emit_model, to=sids)

@socketio.event
def fetch_last_unread_dms():
    headers = get_headers(request, with_device_id)
    user_id = headers["UserId"]
    dms = user_session.query(DM).filter(DM.receiver == user_id, DM.is_read == False).all()
    users_with_new_dms = []
    print(users_with_new_dms)

    for dm in dms:
        if dm.sender in users_with_new_dms:
            pass
        else:
            users_with_new_dms.append(dm.sender)

    dms_json = []
    print(users_with_new_dms)

    for user in users_with_new_dms:
        dm = user_session.query(DM).filter(DM.receiver == user_id, DM.sender == user).order_by(DM.id.desc()).first()

        username = user_session.query(User.username).filter(User.id == dm.sender).one()[0]

        dm_json = {
            'id': dm.id,
            'sender': dm.sender,
            'username': username,
            'receiver': dm.receiver,
            'message': dm.message,
            'date': str(dm.date.isoformat()+'Z'),
            'isRead': dm.is_read
        }

        dms_json.append(dm_json)
    print(dms_json)
    emit('fetch_last_unread_dms', dms_json, to=request.sid)

@socketio.event
def fetch_dms(data):
    headers = get_headers(request, with_device_id)
    user_id = headers["UserId"]

    sender = data.pop('sender')
#    from_id = data.pop('from')
#    to_id = data.pop('to')

    messages = user_session.query(DM).filter(DM.receiver == user_id, DM.sender == sender, DM.is_read == False).order_by(DM.id.desc())
    messages_json = []

    for message in messages:
        username = user_session.query(User.username).filter(User.id == message.sender).one()[0]

        message_json = {
            'id': message.id,
            'username': username,
            'sender': message.sender,
            'receiver': message.receiver,
            'message': message.message,
            'date': str(message.date.isoformat()+'Z'),
            'isRead': message.is_read
        }

        messages_json.append(message_json)

    messages_json.sort(key= lambda i: i['id'])

    emit('fetch_dms', messages_json, to=request.sid)

@socketio.event
def delete_dms(data):
    headers = get_headers(request, with_device_id)
    user_id = headers["UserId"]

    sender = data.pop('sender')
    from_id = data.pop('from')
    to_id = data.pop('to')

    messages = user_session.query(DM).filter(DM.receiver == user_id, DM.sender == sender, DM.id.between(from_id, to_id)).all()

    for message in messages:
        user_session.delete(message)

    user_session.commit()

    emit('delete_dms', {'success': True})
