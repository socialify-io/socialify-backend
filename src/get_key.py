from app import app, HTTP_METHODS, route, key_session, user_session
from flask import Flask, render_template, request, jsonify
from db.keys_db_declarative import KeyBase, Key
from .RSA_helper import encrypt_public_key, generate_keys, decrypt_private_key

# models
from models.errors._api_error import ApiError

from models.responses._error_response import ErrorResponse
from models.responses._response import Response

from models.errors.codes._error_codes import Error

@app.route(f'{route}/getkey', methods=HTTP_METHODS)
async def get_key():
    if request.method != 'POST':
        return render_template('what_are_you_looking_for.html')

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