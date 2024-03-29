from app import app, HTTP_METHODS, route, key_session, user_session
from flask import Flask, render_template, request, jsonify

# Database
from db.keys_db_declarative import Key
from db.users_db_declarative import User

# Helpers
from ..helpers.get_headers import get_headers, with_fingerprint, without_fingerprint
from ..helpers.verify_authtoken import verify_authtoken

# Crypto
from ..helpers.RSA_helper import decrypt_rsa
from Crypto.PublicKey import RSA
import bcrypt

# Models
from models.errors._api_error import ApiError

from models.responses._error_response import ErrorResponse
from models.responses._response import Response
from models.errors.codes._error_codes import Error


@app.route(f'{route}/register', methods=HTTP_METHODS)
async def register():
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

    if verify_authtoken(headers, "register"):
        body = request.get_json(force=True)

        pub_key_string = body['pubKey']

        try:
            priv_key = key_session.query(Key).filter(Key.pub_key == pub_key_string).one()
            priv_key = priv_key.priv_key

        except TypeError:
            error = ApiError(
                code=Error().InvalidPublicRSAKey,
                reason='Invalid public RSA key.'
            ).__dict__

            return jsonify(ErrorResponse(
                errors=[error]).__dict__)

        priv_key = RSA.importKey(priv_key)

        try:
            password = decrypt_rsa(body['password'], priv_key)

        except:
            error = ApiError(
                code=Error().InvalidPasswordEncryption,
                reason='Invalid password encryption.'
            ).__dict__

            return jsonify(ErrorResponse(
                errors=[error]).__dict__)

        repeat_password = decrypt_rsa(body['repeat_password'], priv_key)

        if password == repeat_password:
            users = user_session.query(User.username).all()
            
            if (body['username'],) in users:
                error = ApiError(
                    code = Error().InvalidUsername,
                    reason = 'This username is already taken.'
                ).__dict__

                return jsonify(ErrorResponse(
                            errors = [error]).__dict__)

            else:

                hashed_pass = bcrypt.hashpw(bytes(password, 'utf-8'), bcrypt.gensalt())

                new_user = User(
                    username=body['username'],
                    password=hashed_pass
                )

                user_session.add(new_user)
                user_session.commit()

                key_session.query(Key).filter(Key.pub_key==pub_key_string).delete()
                key_session.commit()

                return jsonify(Response(data={}).__dict__)
        else:
            error = ApiError(
                code = Error().InvalidRepeatPassword,
                reason = 'Passwords are not same.'
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