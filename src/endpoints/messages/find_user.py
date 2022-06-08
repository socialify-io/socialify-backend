from app import socketio, mongo_client
from flask_socketio import emit, send, join_room, leave_room
from flask import request

import hashlib

# Database
from bson.objectid import ObjectId

# Helpers
from ...helpers.get_headers import get_headers, with_device_id, without_device_id
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
def find_user(phrase):
    results = find_users_in_database(phrase.lower())
    response = []

    headers = get_headers(request, with_device_id)
    #username = user_session.query(User.username).filter(User.id == headers["UserId"]).one()[0]

    #username = mongo_client.users.find_one({"_id": ObjectId(headers["UserId"])})["username"]

    for user in results:
        if(user["_id"] != ObjectId(headers["UserId"])):
            json_model = {
                'id': str(user['_id']),
                'username': user['username']
            }
            response.append(json_model)

    print(response)

    emit('find_user', response)

def find_users_in_database(phrase):
    #search = /{}/.format(phrase)
    #results = user_session.query(User.id, User.username).filter(User.username.like(search)).all()
    results = mongo_client.users.find({"username": {"$regex": phrase}})
    return results

