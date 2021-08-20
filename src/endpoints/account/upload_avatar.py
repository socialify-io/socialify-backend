from sqlalchemy.sql.functions import user
from app import app, HTTP_METHODS, route, key_session, user_session
from flask import Flask, render_template, request, jsonify

# Database
from db.users_db_declarative import Device, User

# Helpers
from ...helpers.get_headers import get_headers, with_fingerprint, without_fingerprint
from ...helpers.verify_authtoken import verify_authtoken
from ...helpers.RSA_helper import verify_sign

# Crypto
import base64

# Models
from models.errors._api_error import ApiError

from models.responses._error_response import ErrorResponse
from models.responses._response import Response
from models.errors.codes._error_codes import Error


@app.route(f'{route}/uploadAvatar', methods=HTTP_METHODS)
async def upload_avatar():
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

    if verify_authtoken(headers, 'uploadAvatar'):
        try:
            userId = user_session.query(Device.userId).filter(Device.id == headers['DeviceId']).one()
            userId = int(userId[0])

        except:
            error = ApiError(
                code=Error().InvalidDeviceId,
                reason='Device id is not valid. Device may be deleted.'
            ).__dict__

            return jsonify(ErrorResponse(
                errors=[error]).__dict__)

        pub_key = user_session.query(Device.pubKey).filter(Device.userId == userId, Device.fingerprint == headers["Fingerprint"]).one()

        if verify_sign(request, pub_key, 'uploadAvatar'):
            body = request.get_json(force=True)
            avatar = body['avatar']

            user_session.query(User).filter(User.id == userId).update({'avatar': avatar})
            user_session.commit()

            return jsonify(Response(data={}).__dict__)
            
        else:
            error = ApiError(
                code=Error.InvalidSignature,
                reason='Invalid signature.'
            ).__dict__

            return jsonify(ErrorResponse(
                errors=[error]).__dict__)
