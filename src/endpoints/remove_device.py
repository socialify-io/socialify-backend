from app import app, HTTP_METHODS, route, user_session
from flask import render_template, request, jsonify

# Database
from db.users_db_declarative import Device

# Helpers
from ..helpers.get_headers import get_headers, with_fingerprint, without_fingerprint
from ..helpers.RSA_helper import verify_sign
from ..helpers.verify_authtoken import verify_authtoken

# Crypto
from Crypto.PublicKey import RSA

# Models
from models.errors._api_error import ApiError

from models.responses._error_response import ErrorResponse
from models.responses._response import Response

from models.errors.codes._error_codes import Error


@app.route(f'{route}/removeDevice', methods=HTTP_METHODS)
async def remove_device():
    if request.method != 'POST':
        return render_template('what_are_you_looking_for.html')
    try:
        signature = request.headers['Signature']
        headers = get_headers(request, with_fingerprint)

    except:
        error = ApiError(
            code=Error().InvalidHeaders,
            reason='Some required request headers not found.'
        ).__dict__

        return jsonify(ErrorResponse(
            errors=[error]).__dict__)

    if verify_authtoken(headers, "removeDevice"):
        try:
            userId = user_session.query(Device.userId).filter(Device.fingerprint == headers["Fingerprint"]).one()
            userId = int(userId[0])

        except:
            error = ApiError(
                code=Error().InvalidFingerprint,
                reason='Fingerprint is not valid. Device may be deleted.'
            ).__dict__

            return jsonify(ErrorResponse(
                errors=[error]).__dict__)

        pub_key = user_session.query(Device.pubKey).filter(Device.userId == userId, Device.fingerprint == headers["Fingerprint"]).one()

        if verify_sign(request, pub_key, "removeDevice"):
            try:
                user_session.query(Device).filter(Device.fingerprint == headers["Fingerprint"], Device.deviceName == request.get_json()['device']['deviceName']).delete()
                user_session.commit()

                return jsonify(Response(data={}).__dict__)
            except:
                error = ApiError(
                    code=Error.InvalidRequestPayload,
                    reason='Some params in payload are not valid.'
                ).__dict__

                return jsonify(ErrorResponse(
                    errors=[error]).__dict__)
        else:
            error = ApiError(
                code=Error.InvalidSignature,
                reason='Invalid signature.'
            ).__dict__

            return jsonify(ErrorResponse(
                errors=[error]).__dict__)
