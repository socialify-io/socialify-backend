from sqlalchemy.sql.functions import user
from app import app, HTTP_METHODS, route, key_session, user_session
from flask import Flask, render_template, request, jsonify
import json

# Database
from db.users_db_declarative import Device, User, FriendRequest

# Helpers
from ..helpers.get_headers import get_headers, with_fingerprint, without_fingerprint
from ..helpers.verify_authtoken import verify_authtoken
from ..helpers.RSA_helper import verify_sign

# Crypto
import base64

# Datatime
from datetime import datetime
import pytz

# Models
from models.errors._api_error import ApiError

from models.responses._error_response import ErrorResponse
from models.responses._response import Response
from models.errors.codes._error_codes import Error

@app.route(f'{route}/sendFriendRequest', methods=HTTP_METHODS)
async def send_friend_request():
    if request.method != 'POST':
        return render_template('what_are_you_looking_for.html')
    try:
        headers = get_headers(request, with_fingerprint)

    except:
        error = ApiError(
            code=Error().InvalidHeaders,
            reason='Some required request headers not found.'
        ).__dict__

        return jsonify(ErrorResponse(
            errors=[error]).__dict__)

    if verify_authtoken(headers, 'sendFriendRequest'):
        try:
            user_id = int(user_session.query(Device.userId).filter(Device.id == headers['DeviceId']).one()[0])
            user_username = user_session.query(User.username).filter(User.id == user_id).one()[0]

        except:
            error = ApiError(
                code=Error().InvalidDeviceId,
                reason='Device id is not valid. Device may be deleted.'
            ).__dict__

            return jsonify(ErrorResponse(
                errors=[error]).__dict__)

        pub_key = user_session.query(Device.pubKey).filter(Device.userId ==
                                                           user_id, Device.fingerprint == headers["Fingerprint"]).one()

        if verify_sign(request, pub_key, 'sendFriendRequest'):
            body = request.get_json(force=True)
            date = datetime.utcfromtimestamp(headers['Timestamp']).replace(tzinfo=pytz.utc)

            new_request = FriendRequest(
                receiverId=body['userId'],
                requesterId=user_id,
                requesterUsername=user_username,
                requestDate=date
            )

            user_session.add(new_request)
            user_session.commit()

            return jsonify(Response(data={}).__dict__)

        else:
            error = ApiError(
                code=Error.InvalidSignature,
                reason='Invalid signature.'
            ).__dict__

            return jsonify(ErrorResponse(
                errors=[error]).__dict__)
    else:
        error = ApiError(
            code = Error().InvalidAuthToken,
            reason = 'Your authorization token is not valid.'
        ).__dict__

        return jsonify(ErrorResponse(
                    errors = [error]).__dict__)


@app.route(f'{route}/fetchPendingFriendsRequests', methods=HTTP_METHODS)
async def fetch_pending_friends_requests():
    if request.method != 'POST':
        return render_template('what_are_your_looking_for.html')
    try:
        headers = get_headers(request, with_fingerprint)

    except:
        error = ApiError(
            code=Error().InvalidHeaders,
            reason='Some required headers not found.'
         ).__dict__

        return jsonify(ErrorResponse(errors=[error]).__dict__)

    if verify_authtoken(headers, 'fetchPendingFriendsRequests'):
        try:
            user_id = int(user_session.query(Device.userId).filter(Device.id == headers['DeviceId']).one()[0])

        except:
            error = ApiError(
                code=Error().InvalidDeviceId,
                reason='Device id is not valid. Device may be deleted.'
            ).__dict__

            return jsonify(ErrorResponse(
                errors=[error]).__dict__)

        pub_key = user_session.query(Device.pubKey).filter(Device.userId == user_id, Device.fingerprint == headers["Fingerprint"]).one()

        if verify_sign(request, pub_key, 'fetchPendingFriendsRequests'):
            requests = user_session.query(FriendRequest).filter(FriendRequest.receiverId == user_id).all()
            print(requests)

            return jsonify(Response(data={requests}).__dict__)

        else:
            error = ApiError(
                code=Error.InvalidSignature,
                reason='Invalid signature.'
            ).__dict__

            return jsonify(ErrorResponse(
                errors=[error]).__dict__)
    else:
        error = ApiError(
            code = Error().InvalidAuthToken,
            reason = 'Your authorization token is not valid.'
        ).__dict__

        return jsonify(ErrorResponse(
                    errors = [error]).__dict__)
