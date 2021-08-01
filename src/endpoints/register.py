from app import app, HTTP_METHODS, route, key_session, user_session
from flask import Flask, render_template, request, jsonify
from db.keys_db_declarative import Key
from db.users_db_declarative import User

#models
from models.errors._api_error import ApiError

from models.responses._error_response import ErrorResponse
from models.responses._response import Response
from models.errors.codes._error_codes import Error

# crypto
from ..helpers.RSA_helper import decrypt_rsa

from Crypto.PublicKey import RSA
import bcrypt

auth_token_begin_header = '$begin-register$'
auth_token_end_header = '$end-register$'

@app.route(f'{route}/register', methods=HTTP_METHODS)
async def register():
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