from app import app, route, socketio, mongo_client
from flask_socketio import emit, send, join_room, leave_room
from flask import Flask, render_template, request, jsonify, redirect, url_for
import json

import hashlib

# Helpers
from ...helpers.get_headers import get_headers, with_device_id, without_device_id
from ...helpers.verify_authtoken import verify_authtoken
from ...helpers.RSA_helper import verify_sign
from ...helpers.get_user_id import get_user_id

# Datatime
from datetime import datetime
import pytz
from bson.objectid import ObjectId

# Crypto
import base64

# Images
from PIL import Image
from io import BytesIO
import os

# Models
from models.errors._api_error import ApiError

from models.responses._error_response import ErrorResponse
from models.responses._response import Response

from models.errors.codes._error_codes import Error

@socketio.event
def send_dm(data):
    headers = get_headers(request, with_device_id)
    user_id = headers["UserId"]
    #username = user_session.query(User.username).filter(User.id ==
    #        user_id).one()[0]
    username = mongo_client.users.find_one({"_id": ObjectId(user_id)})["username"]

    receiver_id = data.pop('receiverId')
    message = data.pop('message')
    media = data.pop('media')

    #sids = json.loads(user_session.query(User.sids).filter(User.id == receiver_id).one()[0])
    sids = json.loads(mongo_client.users.find_one({"_id": ObjectId(receiver_id)})["sids"])
    sids.append(request.sid)

    # new_dm = DM(
    #     receiver = receiver_id,
    #     sender = user_id,
    #     message = message,
    #     date = datetime.utcnow().replace(microsecond=0)
    # )

    # user_session.add(new_dm)
    # user_session.commit()

    new_dm = {
        "receiver": receiver_id,
        "sender": user_id,
        "message": message,
        "date": datetime.utcnow().replace(microsecond=0)
    }

    mongo_client.dms.insert_one(new_dm)

    media_parsed = []

    for media_element in media:
        # new_media = Media(
        #     mediaURL = f'{receiver_id}',
        #     type = media_element["type"],
        #     dmId = new_dm.id
        # )

        # user_session.add(new_media)
        # user_session.commit()
        # new_media.mediaURL = f'{new_media.mediaURL}-{new_media.id}'
        # user_session.commit()

        new_media = {
            "mediaURL": f'{receiver_id}',
            "type": media_element["type"],
            "dmId": str(new_dm["_id"])
        }

        mongo_client.media.insert_one(new_media)
        new_media["mediaURL"] = f'{new_media["mediaURL"]}-{new_media["_id"]}'
        mongo_client.media.update_one({"_id": new_media["_id"]}, {"$set": {"mediaURL": new_media["mediaURL"]}})

        new_media_to_append = {
            "id": str(new_media['_id']),
            "mediaURL": f'{receiver_id}',
            "type": media_element["type"],
            "dmId": str(new_dm["_id"])
        }

        media_parsed.append(new_media_to_append)

        if media_element["type"] == 1:
            image = Image.open(BytesIO(base64.b64decode(media_element["media"])))
            image.save(f'{os.path.join(app.config["MEDIA_FOLDER"])}{receiver_id}-{new_media["_id"]}.png', save_all = True)

        media_parsed.append({
            "mediaURL": new_media["mediaURL"],
            "type": new_media["type"]
        })

    emit_model = {
        'id': str(new_dm["_id"]),
        'receiverId': receiver_id,
        'senderId': user_id,
        'message': message,
        'username': username,
        'date': new_dm["date"].isoformat()+'Z',
        'media': media_parsed
    }

    print(emit_model)

    emit('send_dm', emit_model, to=sids)

@socketio.event
def fetch_last_unread_dms():
    headers = get_headers(request, with_device_id)
    user_id = headers["UserId"]
    #dms = user_session.query(DM).filter(DM.receiver == user_id, DM.is_read == False).all()
    dms = mongo_client.dms.find({'receiver': ObjectId(user_id)})
    users_with_new_dms = []
    print(users_with_new_dms)

    for dm in dms:
        if dm['sender'] in users_with_new_dms:
            pass
        else:
            users_with_new_dms.append(dm.sender)

    dms_json = []
    print(users_with_new_dms)

    for user in users_with_new_dms:
        #dm = user_session.query(DM).filter(DM.receiver == user_id, DM.sender == user).order_by(DM.id.desc()).first()
        dm = mongo_client.dms.find_one({'receiver': ObjectId(user_id), 'sender': ObjectId(user)})

        #username = user_session.query(User.username).filter(User.id == dm.sender).one()[0]
        username = mongo_client.users.find_one({"_id": dm["sender"]})["username"]

        dm_json = {
            'id': dm['_id'],
            'sender': dm['sender'],
            'username': username,
            'receiver': dm['receiver'],
            'message': dm['message'],
            'date': str(dm['date'].isoformat()+'Z'),
            'isRead': dm['is_read']
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

    #messages = user_session.query(DM).filter(DM.receiver == user_id, DM.sender == sender, DM.is_read == False).order_by(DM.id.desc())
    messages = mongo_client.dms.find({'receiver': ObjectId(user_id), 'sender': ObjectId(sender), 'is_read': False})

    messages_json = []


    for message in messages:
        #username = user_session.query(User.username).filter(User.id == message.sender).one()[0]
        #media = user_session.query(Media).filter(message.id == Media.dmId).all()
        username = mongo_client.users.find_one({"_id": ObjectId(message["sender"])})["username"]
        media = mongo_client.media.find({"dmId": ObjectId(message["_id"])})

        media_parsed = []

        for media_element in media:
            media_parsed.append({
                "mediaURL": media_element['mediaURL'],
                "type": media_element['type']
            })

        message_json = {
            'id': message['_id'],
            'username': username,
            'sender': message['sender'],
            'receiver': message['receiver'],
            'message': message['message'],
            'date': str(message['date'].isoformat()+'Z'),
            'isRead': message['is_read'],
            'media': media_parsed
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

    #messages = user_session.query(DM).filter(DM.receiver == user_id, DM.sender == sender, DM.id.between(from_id, to_id)).all()
    messages = mongo_client.dms.find({'receiver': ObjectId(user_id), 'sender': ObjectId(sender), '_id': {'$gte': ObjectId(from_id), '$lte': ObjectId(to_id)}})

    for message in messages:
        #user_session.delete(message)
        mongo_client.dms.delete_one({"_id": ObjectId(message["_id"])})

    emit('delete_dms', {'success': True})

@app.route(f'{route}/getMedia/<mediaid>', methods=['GET'])
def get_media(mediaid):
    return(redirect(url_for('static', filename=f'media/{mediaid}.png'), code=301))

