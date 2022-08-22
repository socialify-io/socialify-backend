from app import app, route, socketio, mongo_client, AVATARS_FOLDER
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
from Crypto.Hash import SHA

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

    avatar_for_user = AVATARS_FOLDER + user_id + '.png'

    user_avatar = ""

    if os.path.isfile(avatar_for_user):
        with open(avatar_for_user, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read())
            user_avatar = encoded_string.decode('utf-8')

    receiver_id = data.pop('receiverId')
    media = data.pop('media')

    messages = data['message']

    #sids = json.loads(user_session.query(User.sids).filter(User.id == receiver_id).one()[0])
    sids = mongo_client.users.find_one({"_id": ObjectId(receiver_id)})["sids"]

    # new_dm = DM(
    #     receiver = receiver_id,
    #     sender = user_id,
    #     message = message,
    #     date = datetime.utcnow().replace(microsecond=0)
    # )

    # user_session.add(new_dm)
    # user_session.commit()

    new_dm_messages = []

    for message in messages:
        nonce = message["nonce"]
        tag = message["tag"]
        ciphertext = message["ciphertext"]
        device_id = message["receiverDeviceId"]

        new_dm_for_device = {
            "deviceId": device_id,
            "nonce": nonce,
            "tag": tag,
            "ciphertext": ciphertext,
        }

        new_dm_messages.append(new_dm_for_device)

    new_dm = {
        "receiver": receiver_id,
        "sender": user_id,
        "senderDeviceId": headers["DeviceId"],
        "messages": new_dm_messages,
        "date": datetime.utcnow().replace(microsecond=0),
        "senderNewPublicKey": data["newPublicKey"],
        "isRead": False
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
        'deviceId': headers["DeviceId"],
        'message': new_dm_messages,
        'username': username,
        'avatarHash': str(SHA.new(str(user_avatar).encode('utf-8')).hexdigest()),
        'date': new_dm["date"].isoformat()+'Z',
        'media': media_parsed,
        'senderNewPublicKey': data["newPublicKey"]
    }

    print(emit_model)

    emit('send_dm', emit_model, to=sids)
    
    confirmation_response = {
        'confirmationId': data['confirmationId'],
        'id': str(new_dm['_id']),
        'date': new_dm["date"].isoformat()+'Z'
    }   

    emit("dm_confirmation", confirmation_response, to=request.sid)

@socketio.event
def fetch_all_unread_dms():
    headers = get_headers(request, with_device_id)
    user_id = headers["UserId"]

    dms = mongo_client.dms.find({"receiver": user_id, "isRead": False})
    dms_parsed = []

    for dm in dms:
        #sender = user_session.query(User.username).filter(User.id == dm.sender).one()[0]
        sender_username = mongo_client.users.find_one({"_id": ObjectId(dm["sender"])})["username"]
        sender_avatar = ""

        sender_avatar_for_user = AVATARS_FOLDER + dm["sender"] + '.png'

        if os.path.isfile(sender_avatar_for_user):
            with open(sender_avatar_for_user, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read())
                sender_avatar = encoded_string.decode('utf-8')
        else:
            sender_avatar = ""

        media = mongo_client.media.find({"dmId": ObjectId(dm["_id"])})

        media_parsed = []

        for media_element in media:
            media_parsed.append({
                "mediaURL": media_element['mediaURL'],
                "type": media_element['type']
            })

        dm_parsed = {
            'id': str(dm['_id']),
            'deviceId': dm['senderDeviceId'],
            'username': sender_username,
            'sender': dm['sender'],
            'receiver': dm['receiver'],
            'message': dm['messages'],
            'avatarHash': str(SHA.new(str(sender_avatar).encode('utf-8')).hexdigest()),
            'senderNewPublicKey': dm['senderNewPublicKey'],
            'date': str(dm['date'].isoformat()+'Z'),
            'isRead': dm['isRead'],
            'media': media_parsed
        }

        dms_parsed.append(dm_parsed)

    emit('fetch_all_unread_dms', {'success': True, 'dms': dms_parsed}, to=request.sid)


@socketio.event
def fetch_last_unread_dms():
    headers = get_headers(request, with_device_id)
    user_id = headers["UserId"]
    #dms = user_session.query(DM).filter(DM.receiver == user_id, DM.is_read == False).all()
    dms = mongo_client.dms.find({'receiver': user_id})
    users_with_new_dms = []
    print(users_with_new_dms)

    for dm in dms:
        if dm['sender'] in users_with_new_dms:
            pass
        else:
            users_with_new_dms.append(dm['sender'])

    dms_json = []
    print(users_with_new_dms)

    for user in users_with_new_dms:
        #dm = user_session.query(DM).filter(DM.receiver == user_id, DM.sender == user).order_by(DM.id.desc()).first()
        dm = list(mongo_client.dms.find({'receiver': user_id, 'sender': user}).sort([('_id', -1)]).limit(1))[0]

        if dm["isRead"] == False:
            print(dm)

            #username = user_session.query(User.username).filter(User.id == dm.sender).one()[0]
            username = mongo_client.users.find_one({"_id": ObjectId(dm["sender"])})["username"]

            avatar_for_user = AVATARS_FOLDER + dm['sender'] + '.png'

            user_avatar = ""

            if os.path.isfile(avatar_for_user):
                with open(avatar_for_user, "rb") as image_file:
                    encoded_string = base64.b64encode(image_file.read())
                    user_avatar = encoded_string.decode('utf-8')


            media = mongo_client.media.find({"dmId": ObjectId(dm["_id"])})

            media_parsed = []

            for media_element in media:
                media_parsed.append({
                    "mediaURL": media_element['mediaURL'],
                    "type": media_element['type']
                })

            dm_json = {
                'id': str(dm['_id']),
                'deviceId': dm['senderDeviceId'],
                'username': username,
                'sender': dm['sender'],
                'receiver': dm['receiver'],
                'message': dm['messages'],
                'avatarHash': str(SHA.new(str(user_avatar).encode('utf-8')).hexdigest()),
                'senderNewPublicKey': dm['senderNewPublicKey'],
                'date': str(dm['date'].isoformat()+'Z'),
                'isRead': dm['isRead'],
                'media': media_parsed
            }

            dms_json.append(dm_json)
            mongo_client.dms.update_one({"_id": dm['_id']}, {"$set": {"isRead": True}})

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
    messages = mongo_client.dms.find({'receiver': user_id, 'sender': sender, 'isRead': False})

    messages_json = []

    for message in messages:
        #username = user_session.query(User.username).filter(User.id == message.sender).one()[0]
        #media = user_session.query(Media).filter(message.id == Media.dmId).all()
        username = mongo_client.users.find_one({"_id": ObjectId(message["sender"])})["username"]

        avatar_for_user = AVATARS_FOLDER + message['sender'] + '.png'

        user_avatar = ""

        if os.path.isfile(avatar_for_user):
            with open(avatar_for_user, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read())
                user_avatar = encoded_string.decode('utf-8')


        media = mongo_client.media.find({"dmId": ObjectId(message["_id"])})

        media_parsed = []

        for media_element in media:
            media_parsed.append({
                "mediaURL": media_element['mediaURL'],
                "type": media_element['type']
            })

        message_json = {
            'id': str(message['_id']),
            'deviceId': message['senderDeviceId'],
            'username': username,
            'sender': message['sender'],
            'receiver': message['receiver'],
            'message': message['messages'],
            'avatarHash': str(SHA.new(str(user_avatar).encode('utf-8')).hexdigest()),
            'senderNewPublicKey': message['senderNewPublicKey'],
            'date': str(message['date'].isoformat()+'Z'),
            'isRead': message['isRead'],
            'media': media_parsed
        }

        messages_json.append(message_json)
        mongo_client.dms.update_one({"_id": message['_id']}, {"$set": {"isRead": True}})

    messages_json.sort(key= lambda i: i['id'])

    emit('fetch_dms', messages_json, to=request.sid)

@socketio.event
def get_public_e2e_key(data):
    user_id = data['user']

    keys = mongo_client.devices.find({"userId": ObjectId(user_id)})
    response = []

    for key in keys:
        response.append({
            "deviceId": str(key['_id']),
            "publicKey": str(key['public_e2e_key'])
        })

    emit('get_public_e2e_key', response, to=request.sid)

@socketio.event
def update_public_e2e_key(data):
    headers = get_headers(request, with_device_id)
    user_id = headers["UserId"]
    device_id = headers["DeviceId"]

    public_key = data['key']
    
    mongo_client.devices.update_one({"userId": ObjectId(user_id), "deviceId": ObjectId(device_id)}, {"$set": {"publicKey": public_key}})

    emit('update_public_e2e_key', {"success": True}, to=request.sid)

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

