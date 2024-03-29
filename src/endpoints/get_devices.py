from app import app, HTTP_METHODS, route, user_session
from flask import render_template, request, jsonify

# Database
from db.users_db_declarative import Device

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


@app.route(f'{route}/getDevices', methods=HTTP_METHODS)
async def get_devices():
    if request.method != 'POST':
        return render_template('what_are_you_looking_for.html')

    try:
        signature = request.headers['Signature']
        headers = get_headers(request, with_fingerprint)

    except:
        error = ApiError(
            code = Error().InvalidHeaders,
            reason = 'Some required request headers not found.'
        ).__dict__
        
        return jsonify(ErrorResponse(
                    errors = [error]).__dict__)

    if verify_authtoken(headers, "getDevices"):
        try:
            userId = user_session.query(Device.userId).filter(Device.fingerprint == headers["Fingerprint"]).one()
            userId = int(userId[0])

        except:
            error = ApiError(
                code = Error().InvalidFingerprint,
                reason = 'Fingerprint is not valid. Device may be deleted.'
            ).__dict__

            return jsonify(ErrorResponse(
                        errors = [error]).__dict__)

        pub_key = user_session.query(Device.pubKey).filter(Device.userId == userId, Device.fingerprint == headers["Fingerprint"]).one()
        pub_key = pub_key[0]
        pub_key = RSA.importKey(pub_key)
        
        body = request.get_json()
        if body == None:
            body = {}

        signature_json_check = {
            'headers': headers,
            'body': body,
            'timestamp': headers["Timestamp"],
            'authToken': headers["AuthToken"],
            'endpointUrl': f'{route}/getDevices'
        }

        if verify_sign(signature_json_check, signature, pub_key):
            devices_db = user_session.query(Device).filter(Device.userId == userId).all()
            devices = []

            for device in devices_db:
                device_json = {
                    "deviceName": device.deviceName,
                    "deviceIP": device.deviceIP,
                    "os": device.os,
                    "deviceCreationDate": device.timestamp,
                    "deviceLastActive": device.last_active
                }
                devices.append(device_json)

            return jsonify(Response(data=devices).__dict__)
        else:
            error = ApiError(
                code = Error().InvalidSignature,
                reason = 'Signature is not valid.'
            ).__dict__

            return jsonify(ErrorResponse(
                        errors = [error]).__dict__)

    else:
        error = ApiError(
            code = Error().InvalidAuthToken,
            reason = 'Your authorization token is not valid.'
        ).__dict__

        return jsonify(ErrorResponse(
                    errors = [error]).__dict__)