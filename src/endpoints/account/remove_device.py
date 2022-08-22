from app import app, HTTP_METHODS, route, mongo_client
from flask import render_template, request, jsonify

# Database
from bson.objectid import ObjectId

# Helpers
from ...helpers.get_headers import get_headers, with_device_id, without_device_id
from ...helpers.RSA_helper import verify_sign
from ...helpers.verify_authtoken import verify_authtoken

# Models
from models.errors._api_error import ApiError

from models.responses._error_response import ErrorResponse
from models.responses._response import Response

from models.errors.codes._error_codes import Error


@app.route(f'{route}/removeDevice', methods=['POST'])
async def remove_device():
    try:
        headers = get_headers(request, with_device_id)

    except:
        error = ApiError(
            code=Error().InvalidHeaders,
            reason='Some required request headers not found.'
        ).__dict__

        return jsonify(ErrorResponse(
            error=error).__dict__)

    if verify_authtoken(headers, "removeDevice"):
        user_id = headers['UserId']
        device_id = headers['DeviceId']
        #pub_key = user_session.query(Device.pubKey).filter(Device.userId == user_id, Device.id == device_id).one()
        pub_key = mongo_client.db.devices.find_one({"userId": ObjectId(user_id), "_id": ObjectId(device_id)})

        if verify_sign(request, pub_key, "removeDevice"):
            # user_session.query(Device).filter(Device.id == device_id).delete()
            # user_session.commit()
            mongo_client.db.devices.delete_one({"_id": ObjectId(device_id)})

            return jsonify(Response(data={}).__dict__)

        else:
            error = ApiError(
                code=Error.InvalidSignature,
                reason='Invalid signature.'
            ).__dict__

            return jsonify(ErrorResponse(
                error=error).__dict__)
