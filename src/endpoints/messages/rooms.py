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
    emit('create_room', {'success': True, "data": {"roomId": new_room.id}}, to=request.sid)

@socketio.event
def activate_room(data):
    headers = get_headers(request, with_device_id)
    room_id = data.pop('roomId')
    username = user_session.query(User.username).filter(User.id == headers['UserId']).one().username

    new_message = Message(
        room = room_id,
        is_system_notification = True,
        message = f'Room was created by {username}',
        date = datetime.utcnow().replace(microsecond=0)
    )

    user_session.add(new_message)
    user_session.commit()

    emit_model = {
        "id": new_message.id,
        "roomId": int(room_id),
        "is_system_notification": True,
        "message": new_message.message,
        "username": None,
        "date": str(new_message.date.isoformat()+'Z')
    }

    emit('send_message', emit_model, room=room_id)

@socketio.event
def join_to_room(data):
    headers = get_headers(request, with_device_id)
    user_id = headers['UserId']
    room_id = data.pop('roomId')

    room = user_session.query(Room).filter(Room.id == room_id).one()
    if room == [] or room == None:
        emit('join_to_room', {'success': False, "data": {"error": "Room not found"}}, to=request.sid)
        return
    else:
        if room.is_public:
            if isUserInRoom(room_id, user_id):
                emit('join_to_room', "NE DZIALA AA", to=request.sid)
            else:
                new_member = RoomMember(
                    room=room_id,
                    user=user_id,
                    role=member
                )

                user_session.add(new_member)
                user_session.commit()
                join_room(room_id)
                emit('join_to_room', {"success": True, "data": {"roomName": room.name}}, to=request.sid)

                username = user_session.query(User.username).filter(User.id == user_id).one().username

                new_message = Message(
                    room = room_id,
                    is_system_notification = True,
                    message = f'{username} joined',
                    date = datetime.utcnow().replace(microsecond=0)
                )

                user_session.add(new_message)
                user_session.commit()

                emit_model = {
                    "id": new_message.id,
                    "roomId": int(room_id),
                    "is_system_notification": True,
                    "message": new_message.message,
                    "username": None,
                    "date": str(new_message.date.isoformat()+'Z')
                }

                emit('send_message', emit_model, room=room_id)

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
            "roomId": room_id,
            "message": message,
            "sender": int(user_id),
            "username": username,
            "is_system_notification": False,
            "date": str(new_message.date.isoformat()+'Z')
        }

        emit('send_message', emit_model, room=room_id)
    else:
        emit("send_message", "You are not allowed to send messages to this room")

@socketio.event
def get_informations_about_room(data):
    headers = get_headers(request, with_device_id)
    user_id = headers['UserId']
    room_id = data.pop('roomId')

    if isUserInRoom(room_id, user_id):
        room = user_session.query(Room).filter(Room.id == room_id).one()
        room_members = user_session.query(RoomMember).filter(RoomMember.room == room_id).all()
        room_members_ids = [room_member.user for room_member in room_members]
        room_members_names = [user_session.query(User.username).filter(User.id == room_member_id).one()[0] for room_member_id in room_members_ids]
        room_members_roles = [user_session.query(RoomMember.role).filter(RoomMember.room == room_id, RoomMember.user == room_member_id).one()[0] for room_member_id in room_members_ids]

        room_members_model = [
            {
                "id": room_member_id,
                "username": room_member_name,
                "role": room_member_role
            } for room_member_id, room_member_name, room_member_role in zip(room_members_ids, room_members_names, room_members_roles)
        ]

        emit('get_informations_about_room', {
            "roomId": room.id,
            "isPublic": room.is_public,
            "roomName": room.name,
            "roomMembers": room_members_model
        }, room=room_id)
    else:
        emit("get_informations_about_room", "You are not allowed to get information about this room")

def isUserInRoom(room, user_id):
    isMember = user_session.query(RoomMember).filter(RoomMember.room == room, RoomMember.user == user_id).all()

    return bool(len(isMember))
