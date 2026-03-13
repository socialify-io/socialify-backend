from app import socketio, mongo_client, route, url, app, GROUPS_ICONS_FOLDER
from flask_socketio import emit, send, join_room, leave_room
from flask import request
import json

import hashlib
from datetime import datetime
import base64

# Database
from bson.objectid import ObjectId

# Images
from PIL import Image
from io import BytesIO
import os

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

text = 1
voice = 2

icon_update = 1

@socketio.event
def create_group(data):
    headers = get_headers(request, with_device_id)

    new_group = {
        "_id": ObjectId(),
        "name": data['name'],
        "description": data['description'],
        "type": data['type'],
        "members": [
            {
                "user": headers['UserId'],
                "role": owner,
                "invitedBy": headers['UserId']
            }
        ],
        "rooms": [
            {
                "_id": ObjectId(),
                "sectionName": "Text Rooms",
                "rooms": [
                    {
                        "_id": ObjectId(),
                        "name": "General",
                        "type": text
                    }
                ]
            },
            {
                "_id": ObjectId(),
                "sectionName": "Voice Rooms",
                "rooms": [
                    {
                        "_id": ObjectId(),
                        "name": "General",
                        "type": voice
                    }
                ]
            }
        ],
        "inviteLinks": []
    }

    mongo_client.groups.insert_one(new_group)

    new_group_id = str(new_group['_id'])

    f = Image.open(app.static_folder+ '/images/socialify-logo.png')
    f.save(f'{os.path.join(app.config["GROUPS_ICONS_FOLDER"])}{new_group_id}.png')

    icon_path = f'{os.path.join(app.config["GROUPS_ICONS_FOLDER"])}{new_group_id}.png'
    icon = ""

    if os.path.isfile(icon_path):
        with open(icon_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read())
            icon = encoded_string.decode('utf-8')

    emit('create_group', {'success': True, "data": {"groupId": new_group_id, "icon": icon}}, to=request.sid)

@socketio.event
def create_invite_link(data):
    headers = get_headers(request, with_device_id)

    group = mongo_client.groups.find_one({"_id": ObjectId(data['groupId'])})

    if group is None:
        emit('create_invite_link', {'success': False, "data": {"error": "Group not found"}}, to=request.sid)
        return

    if headers['UserId'] not in [x['user'] for x in group['members']]:
        emit('create_invite_link', {'success': False, "data": {"error": "You are not a member of this group"}}, to=request.sid)
        return

    new_link = {
        "_id": ObjectId(),
        "createdBy": headers['UserId'],
        "linkName": data['linkName'],
        "isAdminApprovalNeeded": data['isAdminApprovalNeeded'],
        "isUnlimitedUses": data['isUnlimitedUses'],
        "isExpiryDateSet": data['isExpiryDateSet'],
        "uses": data['uses'],
        "expiryDate": data['expiryDate'],
        "usedTimes": 0,
        "isForSpecialUsers": data["isForSpecialUsers"],
        "specialUsers": data["specialUsers"]
    }

    hex_id = str(new_link['_id']).encode().hex()
    b64_id = base64.b64encode(bytes.fromhex(hex_id)).decode('utf-8')

    link = f'{url}/{str(b64_id)}'

    mongo_client.groups.update_one({"_id": ObjectId(data['groupId'])}, {"$set": {}, "$push": {"inviteLinks": new_link}}, upsert = True)
    emit('create_invite_link', {'success': True, "data": {"link": link}}, to=request.sid)

@socketio.event
def get_info_about_invite_link(data):
    headers = get_headers(request, with_device_id)

    linkId = data['link'].replace('http://', '').replace('https://', '').replace(':80', '').replace(':443', '').replace(f'{url}/', '')

    intId = base64.b64decode(linkId)
    hexId = bytes(intId).hex()

    group = mongo_client.groups.find_one({"inviteLinks._id": ObjectId(hexId)})

    icon_path = f'{os.path.join(app.config["GROUPS_ICONS_FOLDER"])}{group["_id"]}.png'
    icon = ""

    if os.path.isfile(icon_path):
        with open(icon_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read())
            icon = encoded_string.decode('utf-8')

    return_data = {
        "groupId": str(group['_id']),
        "linkId": linkId,
        "name": group['name'],
        "description": group['description'],
        "icon": icon
    }

    emit('get_info_about_invite_link', {'success': True, "data": return_data}, to=request.sid)

@socketio.event
def get_invite_links(data):
    headers = get_headers(request, with_device_id)

    group = mongo_client.groups.find_one({"_id": ObjectId(data['groupId'])})

    if group is None:
        emit('get_invite_links', {'success': False, "data": {"error": "Group not found"}}, to=request.sid)
        return

    if headers['UserId'] not in [x['user'] for x in group['members']]:
        emit('get_invite_links', {'success': False, "data": {"error": "You are not a member of this group"}}, to=request.sid)
        return

    #TODO: check if user is admin

    links = [{
        "id": str(x['_id']),
        "linkName": x['linkName'],
        "link": f'{url}/{base64.b64encode(bytes.fromhex(str(x["_id"]))).decode("utf-8")}',
        "isAdminApprovalNeeded": x['isAdminApprovalNeeded'],
        "isUnlimitedUses": x['isUnlimitedUses'],
        "isExpiryDateSet": x['isExpiryDateSet'],
        "uses": x['uses'],
        "expiryDate": x['expiryDate'],
        "usedTimes": x['usedTimes'],
        "isForSpecialUsers": x["isForSpecialUsers"],
        "specialUsers": x["specialUsers"]
    } for x in group['inviteLinks']]

    emit('get_invite_links', {'success': True, 'data': {'links': links}}, to=request.sid)

@socketio.event
def join_group(data):
    headers = get_headers(request, with_device_id)

    # linkId = data['link'].replace('invite', '').replace('/', '').replace('http://', '').replace('https://', '').replace(':80', '').replace(':443', '').replace(url, '')

    intId = base64.b64decode(data['linkId'])
    hexId = bytes(intId).hex()

    group = mongo_client.groups.find_one({"inviteLinks._id": ObjectId(hexId)})

    if group is None:
        emit('join_group', {'success': False, "data": {"error": "Group not found"}}, to=request.sid)
        return

    if headers['UserId'] in [x['user'] for x in group['members']]:
        emit('join_group', {'success': False, "data": {"error": "You are already a member of this group"}}, to=request.sid)
        return

    if ObjectId(hexId) in [ObjectId(x["_id"]) for x in group["inviteLinks"]]:

        new_member = {
            "user": headers['UserId'],
            "role": member,
            "joinedFromLink": data["linkId"]
        }

        #TODO count link uses

        icon_path = f'{os.path.join(app.config["GROUPS_ICONS_FOLDER"])}{group["_id"]}.png'
        icon = ""

        if os.path.isfile(icon_path):
            with open(icon_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read())
                icon = encoded_string.decode('utf-8')

        emit_model = {
            'groupId': str(group['_id']),
            'groupName': group['name'],
            'groupDescription': group['description'],
            'icon': icon
        }

        mongo_client.groups.update_one({"_id": group['_id']}, {"$set": {}, "$push": {"members": new_member}})
        emit('join_group', {'success': True, "data": emit_model}, to=request.sid)
    else:
        emit('join_group', {'success': False, "data": {"error": "Invalid invite link"}}, to=request.sid)

@socketio.event
def get_group_rooms(data):
    headers = get_headers(request, with_device_id)

    group = mongo_client.groups.find_one({"_id": ObjectId(data['groupId'])})

    if group is None:
        emit('get_group_rooms', {'success': False, "data": {"error": "Group not found"}}, to=request.sid)
        return

    if headers['UserId'] not in [x['user'] for x in group['members']]:
        emit('get_group_rooms', {'success': False, "data": {"error": "You are not a member of this group"}}, to=request.sid)
        return

    rooms = group['rooms']

    for section in rooms:
        section['_id'] = str(section['_id'])
        for room in section['rooms']:
            room['_id'] = str(room['_id'])

    print("-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-")
    print(rooms)
    print("-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-")

    emit('get_group_rooms', {'success': True, 'data': rooms}, to=request.sid)

@socketio.event
def create_rooms_section(data):
    headers = get_headers(request, with_device_id)

    group = mongo_client.groups.find_one({"_id": ObjectId(data['groupId'])})

    if group is None:
        emit('create_rooms_section', {'success': False, "data": {"error": "Group not found"}}, to=request.sid)
        return

    if headers['UserId'] not in [x['user'] for x in group['members']]:
        emit('create_rooms_section', {'success': False, "data": {"error": "You are not a member of this group"}}, to=request.sid)
        return

    new_section = {
        "_id": ObjectId(),
        "sectionName": data['name'],
        "rooms": []
    }

    mongo_client.groups.update_one({"_id": group['_id']}, {"$set": {}, "$push": {"rooms": new_section}})

    emit('create_rooms_section', {'success': True, "data": {"sectionId": str(new_section['_id'])}}, to=request.sid)

@socketio.event
def create_room(data):
    headers = get_headers(request, with_device_id)

    group = mongo_client.groups.find_one({"_id": ObjectId(data['groupId'])})

    if group is None:
        emit('create_room', {'success': False, "data": {"error": "Group not found"}}, to=request.sid)
        return

    if headers['UserId'] not in [x['user'] for x in group['members']]:
        emit('create_room', {'success': False, "data": {"error": "You are not a member of this group"}}, to=request.sid)
        return

    new_room = {
        "_id": ObjectId(),
        "name": data['name'],
        "type": data['type']
    }

    mongo_client.groups.update_one({"_id": group['_id'], "rooms._id": ObjectId(data['sectionId'])}, {"$set": {}, "$push": {"rooms.$.rooms": new_room}})

    emit('create_room', {'success': True, "data": {"roomId": str(new_room['_id'])}}, to=request.sid)

@socketio.event
def delete_room(data):
    headers = get_headers(request, with_device_id)

    group = mongo_client.groups.find_one({"_id": ObjectId(data['groupId'])})

    if group is None:
        emit('delete_room', {'success': False, "data": {"error": "Group not found"}}, to=request.sid)
        return

    if headers['UserId'] not in [x['user'] for x in group['members']]:
        emit('delete_room', {'success': False, "data": {"error": "You are not a member of this group"}}, to=request.sid)
        return

    mongo_client.groups.update_one({"_id": group['_id'], "rooms._id": ObjectId(data['sectionId'])}, {"$set": {}, "$pull": {"rooms.$.rooms": {"_id": ObjectId(data['roomId'])}}})

    emit('delete_room', {'success': True}, to=request.sid)

@socketio.event
def get_group_members(data):
    headers = get_headers(request, with_device_id)

    group = mongo_client.groups.find_one({"_id": ObjectId(data['groupId'])})

    if group is None:
        emit('get_group_members', {'success': False, "data": {"error": "Group not found"}}, to=request.sid)
        return

    if headers['UserId'] not in [x['user'] for x in group['members']]:
        emit('get_group_members', {'success': False, "data": {"error": "You are not a member of this group"}}, to=request.sid)
        return

    members = []

    for member in group['members']:
        id = str(member['user'])
        role = member['role']
        username = mongo_client.users.find_one({"_id": ObjectId(id)})['username']
        members.append({
            "_id": id,
            "username": username,
            "role": role
        })

    emit('get_group_members', {'success': True, 'data': members}, to=request.sid)

@socketio.event
def update_icon(data):
    headers = get_headers(request, with_device_id)

    group = mongo_client.groups.find_one({"_id": ObjectId(data['groupId'])})

    if group is None:
        emit('update_icon', {'success': False, "data": {"error": "Group not found"}}, to=request.sid)
        return

    if headers['UserId'] not in [x['user'] for x in group['members']]:
        emit('update_icon', {'success': False, "data": {"error": "You are not a member of this group"}}, to=request.sid)
        return

    for member in group['members']:
        if member['user'] == headers['UserId']:
            if member['role'] != owner:
                emit('update_icon', {'success': False, "data": {"error": "You are not an owner of this group"}}, to=request.sid)
                return

    icon = data['icon']

    icon_for_group = GROUPS_ICONS_FOLDER + str(group['_id']) + '.png'

    if os.path.isfile(icon_for_group):
        os.remove(icon_for_group)

    image = Image.open(BytesIO(base64.b64decode(icon)))
    image.save(icon_for_group, save_all = True)

    emit('update_icon', {'success': True}, to=request.sid)

    new_message = {
        "_id": ObjectId(),
        "group": data['groupId'],
        "isSystemNotification": True,
        "timestamp": datetime.utcnow().replace(microsecond=0),
        "type": icon_update
    }

    mongo_client.messages.insert_one(new_message)
    members = [x['user'] for x in group['members']]
    members_sids = [request.sid]
    for x in members:
        for sid in mongo_client.users.find_one({"_id": ObjectId(x)})["sids"]:
            members_sids.append(sid)

    new_message['_id'] = str(new_message['_id'])
    new_message['timestamp'] = new_message['timestamp'].isoformat()+'Z'

    emit('send_message', new_message, to=members_sids)

@socketio.event
def get_group_icon(data):
    headers = get_headers(request, with_device_id)

    group = mongo_client.groups.find_one({"_id": ObjectId(data['groupId'])})

    if group is None:
        emit('get_group_icon', {'success': False, "data": {"error": "Group not found"}}, to=request.sid)
        return

    if headers['UserId'] not in [x['user'] for x in group['members']]:
        emit('get_group_icon', {'success': False, "data": {"error": "You are not a member of this group"}}, to=request.sid)
        return

    icon_path = f'{os.path.join(app.config["GROUPS_ICONS_FOLDER"])}{group["_id"]}.png'
    icon = ""

    if os.path.isfile(icon_path):
        with open(icon_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read())
            icon = encoded_string.decode('utf-8')

            emit('get_group_icon', {'success': True, 'icon': icon}, to=request.sid)
    else:
        emit('get_group_icon', {'success': False, "data": {"error": "Icon not found"}}, to=request.sid)

@socketio.event
def send_message(data):
    headers = get_headers(request, with_device_id)

    group = mongo_client.groups.find_one({"_id": ObjectId(data['groupId'])})

    if group is None:
        emit('send_message', {'success': False, "data": {"error": "Group not found"}}, to=request.sid)
        return

    if headers['UserId'] not in [x['user'] for x in group['members']]:
        emit('send_message', {'success': False, "data": {"error": "You are not a member of this group"}}, to=request.sid)
        return

    #TODO: Add check is room a text room

    username = mongo_client.users.find_one({"_id": ObjectId(headers['UserId'])})['username']

    new_message = {
        "_id": ObjectId(),
        "sender": headers['UserId'],
        "username": username,
        "group": data['groupId'],
        "room": data['roomId'],
        "message": data['message'],
        "isSystemNotification": False,
        "timestamp": datetime.utcnow().replace(microsecond=0),
        "isReadBy": []
    }

    mongo_client.messages.insert_one(new_message)
    members = [x['user'] for x in group['members']]
    members_sids = [request.sid]
    for x in members:
        for sid in mongo_client.users.find_one({"_id": ObjectId(x)})["sids"]:
            members_sids.append(sid)

    new_message['_id'] = str(new_message['_id'])
    new_message['timestamp'] = new_message['timestamp'].isoformat()+'Z'

    emit('send_message', new_message, to=members_sids)

