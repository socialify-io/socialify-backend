from app import app, HTTP_METHODS, route, key_session
from flask import render_template, request, jsonify

# Database
from db.keys_db_declarative import Key

# Helpers
from ..helpers.RSA_helper import generate_keys
from ..helpers.get_headers import get_headers, with_fingerprint, without_fingerprint
from ..helpers.verify_authtoken import verify_authtoken

# Models
from models.errors._api_error import ApiError

from models.responses._error_response import ErrorResponse
from models.responses._response import Response

from models.errors.codes._error_codes import Error


@app.route(f'{route}/getKey', methods=HTTP_METHODS)
async def get_key():
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

    if verify_authtoken(headers, "getKey"):
        key = generate_keys()

        pub_key = key.publickey().exportKey().decode('utf-8')
        priv_key = key.exportKey().decode('utf-8')

        new_key = Key(
            pub_key = pub_key,
            priv_key = priv_key
            )

        key_session.add(new_key)
        key_session.commit()

        response = Response(
            data={
                "pubKey": f'{pub_key}'
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