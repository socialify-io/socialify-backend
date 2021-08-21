from app import socketio, user_session
from flask_socketio import emit, send, join_room, leave_room
from flask import request

import hashlib

# Database
from db.users_db_declarative import Device, User

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
def find_user(data):
    results = find_users_in_database(data['username'])
    response = []

    for user in results:
        json_model = {
            'id': user[0]
            'username': user[1],
            'avatar': user[2]
        }
        response.append(json_model)

    emit('find_user', response)

def find_users_in_database(phrase):
    search = "%{}%".format(phrase)
    #posts = Post.query.fiter(Post.tags.like(search)).all()
    results = user_session.query(User.id, User.username, User.avatar).filter(User.username.like(search)).all()
    return results

