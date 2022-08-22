from app import app, socketio, HTTP_METHODS, route, mongo_client, AVATARS_FOLDER
from flask import render_template, request, jsonify
from flask_socketio import emit
import os

# Database
from bson.objectid import ObjectId

# Helpers
from ..helpers.get_headers import get_headers, with_device_id, without_device_id
from ..helpers.verify_authtoken import verify_authtoken
from ..helpers.RSA_helper import verify_sign

# Crypto
from Crypto.PublicKey import RSA
import base64
from Crypto.Hash import SHA

# Models
from models.errors._api_error import ApiError
from models.responses._error_response import ErrorResponse
from models.responses._response import Response
from models.errors.codes._error_codes import Error
from models._status_codes import Status

@socketio.event
def get_information_about_account(id):
    #user = user_session.query(User).filter(User.id == id).one()
    user = mongo_client.users.find_one({"_id": ObjectId(id)})

    avatar_for_user = AVATARS_FOLDER + str(user['_id']) + '.png'

    user_avatar = ""

    if os.path.isfile(avatar_for_user):
        with open(avatar_for_user, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read())
            user_avatar = encoded_string.decode('utf-8')

    response = {
        "username": str(user['username']),
        "id": str(user['_id']),
        "bio": str(user['bio']),
        "avatar": str(user_avatar),
        "avatarHash": str(SHA.new(str(user_avatar).encode('utf-8')).hexdigest())
    }

    emit('get_information_about_account', response, to=request.sid)

@socketio.event
def search_for_user(phrase):
    user = mongo_client.users.find_one({"username": phrase})

    avatar_for_user = AVATARS_FOLDER + str(user['_id']) + '.png'

    user_avatar = ""

    if os.path.isfile(avatar_for_user):
        with open(avatar_for_user, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read())
            user_avatar = encoded_string.decode('utf-8')

    response = {
        "_id": str(user['_id']),
        "username": str(user['username']),
        "bio": str(user['bio']),
        "avatar": str(user_avatar),
        "avatarHash": str(SHA.new(str(user_avatar).encode('utf-8')).hexdigest())
    }

    emit('search_for_user', {'success': True, 'user': response}, to=request.sid)

@app.route(f'{route}/getInformationAboutAccount', methods=['GET'])
async def get_information_about_account_http():
    try:
        headers = get_headers(request, without_device_id)

    except:
        error = ApiError(
            code = Error().InvalidHeaders,
            reason = 'Some required request headers not found.'
        ).__dict__

        return jsonify(ErrorResponse(
                    error=error).__dict__)

    if verify_authtoken(headers, 'getInformationAboutAccount'):
        body = request.get_json(force=True)
        user_id = body['userId']

        #user = user_session.query(User).filter(User.id == user_id).one()
        user = mongo_client.users.find_one({"_id": ObjectId(user_id)})

        response = Response(
            data = {
                "username": str(user['username']),
                "id": str(user['_id'])
            }
        )

        return jsonify(response.__dict__)

    else:
        error = ApiError(
            code = Error().InvalidAuthToken,
            reason = 'Your authorization token is not valid.'
        ).__dict__

        return jsonify(ErrorResponse(
                    error=error).__dict__)
