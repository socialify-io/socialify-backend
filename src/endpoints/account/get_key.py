from app import app, HTTP_METHODS, route, key_session
from flask import render_template, request, jsonify

# Database
from db.keys_db_declarative import Key

# Helpers
from ...helpers.RSA_helper import generate_keys
from ...helpers.get_headers import get_headers, with_device_id, without_device_id
from ...helpers.verify_authtoken import verify_authtoken

# Models
from models.errors._api_error import ApiError

from models.responses._error_response import ErrorResponse
from models.responses._response import Response

from models.errors.codes._error_codes import Error


@app.route(f'{route}/getKey', methods=['GET'])
async def get_key():
    try:
        headers = get_headers(request, without_device_id)

    except:
        error = ApiError(
            code = Error().InvalidHeaders,
            reason = 'Some required request headers not found.'
        ).__dict__

        return jsonify(ErrorResponse(
                    error = error).__dict__)

    print(headers)

    if 'text/html' in headers['Accept']:
        return render_template('what_are_you_looking_for.html')

    if verify_authtoken(headers, "getKey"):
        key = generate_keys()

        pub_key = key.publickey().exportKey().decode('utf-8')
        priv_key = key.exportKey().decode('utf-8')

        clear_pub_key = pub_key.replace('\n', '').replace('-----BEGIN PUBLIC KEY-----', '').replace('-----END PUBLIC KEY-----', '')

        new_key = Key(
            pub_key = clear_pub_key,
            priv_key = priv_key,
            )

        key_session.add(new_key)
        key_session.commit()

        response = Response(
            data={
                "pubKey": f'{clear_pub_key}'
            }
        )

        return jsonify(response.__dict__)

    else:
        error = ApiError(
            code = Error().InvalidAuthToken,
            reason = 'Your authorization token is not valid.'
        ).__dict__

        return jsonify(ErrorResponse(
                    error = error).__dict__)
