from app import app, HTTP_METHODS, route, key_session, user_session
from flask import Flask, render_template, request, jsonify
from db.keys_db_declarative import KeyBase, Key
from .RSA_helper import encrypt_public_key, generate_keys, decrypt_private_key

import bcrypt

# models
from models.errors._api_error import ApiError

from models.responses._error_response import ErrorResponse
from models.responses._response import Response

from models.errors.codes._error_codes import Error

auth_token_begin_header = '$begin-getKey$'
auth_token_end_header = '$end-getKey$'

@app.route(f'{route}/getKey', methods=HTTP_METHODS)
async def get_key():
    if request.method != 'POST':
        return render_template('what_are_you_looking_for.html')

    try:
        user_agent = request.headers['User-Agent']
        os = request.headers['OS']
        timestamp = request.headers['Timestamp']
        app_version = request.headers['AppVersion']
        auth_token = bytes(request.headers['AuthToken'], 'utf-8')

    except:
        error = ApiError(
            code = Error().InvalidHeaders,
            reason = 'Some required request headers not found.'
        ).__dict__
        
        return jsonify(ErrorResponse(
                    errors = [error]).__dict__)

    auth_token_check = bytes(f'{auth_token_begin_header}.{app_version}+{os}+{user_agent}#{timestamp}#.{auth_token_end_header}', 'utf-8')

    if bcrypt.checkpw(auth_token_check, auth_token):
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