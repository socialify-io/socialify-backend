from app import app, HTTP_METHODS, route, user_session
from flask import render_template, request, jsonify

# Database
from db.users_db_declarative import Device

# Helpers
from ...helpers.get_headers import get_headers, with_device_id, without_device_id
from ...helpers.verify_authtoken import verify_authtoken
from ...helpers.RSA_helper import verify_sign

# Crypto
from Crypto.PublicKey import RSA

# Models
from models.errors._api_error import ApiError
from models.responses._error_response import ErrorResponse
from models.responses._response import Response
from models.errors.codes._error_codes import Error
from models._status_codes import Status


@app.route(f'{route}/getDevices', methods=['GET'])
async def get_devices():
    try:
        headers = get_headers(request, with_device_id)

    except:
        error = ApiError(
            code = Error().InvalidHeaders,
            reason = 'Some required request headers not found.'
        ).__dict__

        return jsonify(ErrorResponse(
                    error=error).__dict__)

    if verify_authtoken(headers, "getDevices"):
        user_id = headers["UserId"]
        device_id = headers["DeviceId"]

        pub_key = user_session.query(Device.pubKey).filter(Device.userId == user_id, Device.id == device_id).one()

        if verify_sign(request, pub_key, "getDevices"):
            devices_db = user_session.query(Device).filter(Device.userId == user_id).all()
            devices = []

            for device in devices_db:
                device_json = {
                    "deviceName": device.deviceName,
                    "deviceIP": device.deviceIP,
                    "os": device.os,
                    "deviceCreationDate": device.timestamp,
                    "deviceLastActive": device.last_active,
                    "status": device.status
                }
                devices.append(device_json)

            return jsonify(Response(data=devices).__dict__)
        else:
            error = ApiError(
                code = Error().InvalidSignature,
                reason = 'Signature is not valid.'
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
