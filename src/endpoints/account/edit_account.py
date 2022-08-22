from sqlalchemy.sql.functions import user
from flask_socketio import emit
from app import app, HTTP_METHODS, route, mongo_client, socketio, mongo_client, AVATARS_FOLDER
from flask import Flask, render_template, request, jsonify, redirect, url_for

# Database
from bson.objectid import ObjectId

# Helpers
from ...helpers.get_headers import get_headers, with_device_id, without_device_id
from ...helpers.verify_authtoken import verify_authtoken
from ...helpers.RSA_helper import verify_sign

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
def update_bio(data):
    headers = get_headers(request, with_device_id)

    new_bio = data['bio']

    if len(new_bio) >= 50:
       emit('update_bio', {'success': False, 'error': 'Bio must be less than 50 characters.'})
       return

    mongo_client.users.update_one({'_id': ObjectId(headers['UserId'])}, {'$set': {'bio': new_bio}})

    emit('update_bio', {'success': True})

@socketio.event
def get_user_data(data):
    headers = get_headers(request, with_device_id)

    user_data = mongo_client.users.find_one({'_id': ObjectId(headers['UserId'])})

    user_data['_id'] = str(user_data['_id'])
    avatar_for_user = AVATARS_FOLDER + user_data['_id'] + '.png'

    if os.path.isfile(avatar_for_user):
        with open(avatar_for_user, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read())
            user_data['avatar'] = encoded_string.decode('utf-8')

    user_data.update({'avatarHash': SHA.new(str(user_data['avatar']).encode('utf-8')).hexdigest()})

    emit('get_user_data', {'success': True, 'user_data': user_data})

@socketio.event
def upload_avatar(data):
    headers = get_headers(request, with_device_id)

    avatar = data['avatar']

    avatar_for_user = AVATARS_FOLDER + headers['UserId'] + '.png'

    if os.path.isfile(avatar_for_user):
        os.remove(avatar_for_user)

    image = Image.open(BytesIO(base64.b64decode(avatar)))
    image.save(avatar_for_user, save_all = True)

    emit('upload_avatar', {'success': True})


@app.route(f'{route}/uploadAvatar', methods=['UPDATE', 'POST'])
async def upload_avatar():
    try:
        headers = get_headers(request, with_device_id)

    except:
        error = ApiError(
            code=Error().InvalidHeaders,
            reason='Some required request headers not found.'
        ).__dict__

        return jsonify(ErrorResponse(
            error=error).__dict__)

    if verify_authtoken(headers, 'uploadAvatar'):
        user_id = headers["UserId"]
        device_id = headers["DeviceId"]

        #pub_key = user_session.query(Device.pubKey).filter(Device.userId == user_id, Device.id == device_id).one()
        pub_key = mongo_client.db.devices.find_one({"userId": ObjectId(user_id), "_id": ObjectId(device_id)})

        if verify_sign(request, pub_key, 'uploadAvatar'):
            body = request.get_json(force=True)
            avatar = body['avatar']

            image = Image.open(BytesIO(base64.b64decode(avatar)))
            image.save(f'{os.path.join(app.config["AVATARS_FOLDER"])}{user_id}.png', save_all = True)

            return jsonify(Response(data={}).__dict__)

        else:
            error = ApiError(
                code=Error.InvalidSignature,
                reason='Invalid signature.'
            ).__dict__

            return jsonify(ErrorResponse(
                error=error).__dict__)
    else:
        error = ApiError(
            code = Error().InvalidAuthToken,
            reason = 'Your authorization token is not valid.'
        ).__dict__

        return jsonify(ErrorResponse(
                    error=error).__dict__)

@app.route(f'{route}/getAvatar/<user_id>', methods=['GET'])
def get_avatar(user_id):
    return(redirect(url_for('static', filename=f'avatars/{user_id}.png'), code=301))

