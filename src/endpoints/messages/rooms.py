from app import socketio, user_session, route
from flask_socketio import emit, send, join_room, leave_room
from flask import request

import hashlib
from datetime import datetime

# Database
from db.users_db_declarative import Device, User, Room, RoomMember, Message

# Helpers
from ...helpers.get_headers import get_headers, with_device_id, without_device_id
from ...helpers.verify_authtoken import verify_authtoken
from ...helpers.RSA_helper import verify_sign

# Models
from models.errors._api_error import ApiError

from models.responses._error_response import ErrorResponse
from models.responses._response import Response

from models.errors.codes._error_codes import Error

owner = 1
member = 2

@socketio.event
def create_room(data):
    headers = get_headers(request, with_device_id)
    new_room = Room(
        name=data.pop('roomName'),
        is_public=True,
        password=None
    )
    user_session.add(new_room)
    user_session.commit()

    new_room_member = RoomMember(
        room=new_room.id,
        user=headers['UserId'],
        role=owner
    )
    user_session.add(new_room_member)
    user_session.commit()
    join_room(new_room.id)
    emit('create', {'success': True}, to=request.sid)

@socketio.event
def join_to_room(data):
    headers = get_headers(request, with_device_id)
    user_id = headers['UserId']
    room_id = data.pop('roomId')

    room = user_session.query(Room).filter(Room.id == room_id).one()
    if room.is_public:
        new_member = RoomMember(
            room=room_id,
            user=user_id,
            role=member
        )

        user_session.add(new_member)
        user_session.commit()
        join_room(room_id)
        emit('join_room', {"success": True}, to=request.sid)

    else:
        emit("join_room", "You are not allowed to join this room")

@socketio.event
def connect_room(data):
    headers = get_headers(request, with_device_id)
    user_id = headers['UserId']
    room_id = data.pop('roomId')

    isMember = user_session.query(RoomMember).filter(RoomMember.room == room_id, RoomMember.user == user_id).one()

    if isMember:
        join_room(room_id)
        emit('connect_room', {"success": True}, to=request.sid)
    else:
        emit("connect_room", "You are not allowed to connect to this room")

@socketio.event
def send_message(data):
    headers = get_headers(request, with_device_id)
    user_id = headers['UserId']
    room_id = data.pop('roomId')

    if isUserInRoom(room_id, user_id):
        message = data.pop('message')
        username = user_session.query(User.username).filter(User.id == user_id).one()[0]

        new_message = Message(
            room = room_id,
            sender = user_id,
            message = message,
            date = datetime.utcnow().replace(microsecond=0)
        )

        user_session.add(new_message)
        user_session.commit()

        emit_model = {
            "id": new_message.id,
            "message": message,
            "sender": user_id,
            "username": username,
            "date": str(new_message.date.isoformat()+'Z')
        }

        emit('send_message', emit_model, room=room_id)
    else:
        emit("send_message", "You are not allowed to send messages to this room")

def isUserInRoom(room, user_id):
    isMember = user_session.query(RoomMember).filter(RoomMember.room == room, RoomMember.user == user_id).one()
    if isMember:
        return True
    else:
        return False
