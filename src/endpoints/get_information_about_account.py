from app import app, socketio, HTTP_METHODS, route, user_session
from flask import render_template, request, jsonify
from flask_socketio import emit

# Database
from db.users_db_declarative import User

# Helpers
from ..helpers.get_headers import get_headers, with_fingerprint, without_fingerprint
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
    user = user_session.query(User).filter(User.id == id).one()

    response = {
        "username": str(user.username),
        "id": str(user.id)
    }

    emit('get_information_about_account', response, to=request.sid)

@app.route(f'{route}/getInformationAboutAccount', methods=HTTP_METHODS)
async def get_information_about_account_http():
    if request.method != 'POST':
        return render_template('what_are_you_looking_for.html')

    try:
        headers = get_headers(request, without_fingerprint)

    except:
        error = ApiError(
            code = Error().InvalidHeaders,
            reason = 'Some required request headers not found.'
        ).__dict__

        return jsonify(ErrorResponse(
                    errors = [error]).__dict__)

    if verify_authtoken(headers, 'getInformationAboutAccount'):
        body = request.get_json(force=True)
        id = body['userId']

        user = user_session.query(User).filter(User.id == id).one()

        response = Response(
            data = {
                "username": str(user.username),
                "id": str(user.id)
            }
        )

        return jsonify(response.__dict__)

    else:
        error = ApiError(
            code = Error().InvalidAuthToken,
            reason = 'Your authorization token is not valid.'
        ).__dict__

        return jsonify(ErrorResponse(
                    errors = [error]).__dict__)

