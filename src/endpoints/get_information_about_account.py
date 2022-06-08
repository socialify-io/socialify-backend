from app import app, socketio, HTTP_METHODS, route, mongo_client
from flask import render_template, request, jsonify
from flask_socketio import emit

# Database
from bson.objectid import ObjectId

# Helpers
from ..helpers.get_headers import get_headers, with_device_id, without_device_id
from ..helpers.verify_authtoken import verify_authtoken
from ..helpers.RSA_helper import verify_sign

# Crypto
from Crypto.PublicKey import RSA

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

    response = {
        "username": str(user['username']),
        "id": str(user['_id'])
    }

    emit('get_information_about_account', response, to=request.sid)

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

