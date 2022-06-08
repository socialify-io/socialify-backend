from sqlalchemy.sql.functions import user
from app import app, HTTP_METHODS, route, mongo_client 
from flask import Flask, render_template, request, jsonify, redirect, url_for

# Database
from bson.objectid import ObjectId

# Helpers
from ...helpers.get_headers import get_headers, with_device_id, without_device_id
from ...helpers.verify_authtoken import verify_authtoken
from ...helpers.RSA_helper import verify_sign

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

