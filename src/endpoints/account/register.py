from app import app, HTTP_METHODS, route, mongo_client
from flask import Flask, render_template, request, jsonify

# Helpers
from ...helpers.get_headers import get_headers, with_device_id, without_device_id
from ...helpers.verify_authtoken import verify_authtoken
from ...helpers.RSA_helper import decrypt_rsa

# Crypto
from Crypto.PublicKey import RSA
import bcrypt
import base64
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.serialization import load_pem_public_key, load_pem_private_key
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes

# Images
from PIL import Image
import os

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
        headers = get_headers(request, without_device_id)

    except:
        error = ApiError(
            code = Error().InvalidHeaders,
            reason = 'Some required request headers not found.'
        ).__dict__

        return jsonify(ErrorResponse(
                    error = error).__dict__)

    if verify_authtoken(headers, 'register'):
        body = request.get_json(force=True)

        pub_key_string = body['pubKey']

        try:
            #priv_key = key_session.query(LoginKey).filter(LoginKey.pub_key == pub_key_string).one()
            #priv_key = priv_key.priv_key

            priv_key = mongo_client.login_keys.find_one({'pub_key': pub_key_string})['priv_key']

        except TypeError:
            error = ApiError(
                code=Error().InvalidPublicRSAKey,
                reason='Invalid public ECC key.'
            ).__dict__

            return jsonify(ErrorResponse(
                error=error).__dict__)

        #priv_key = RSA.importKey(priv_key)

        priv_key = load_pem_private_key(bytes(priv_key, 'utf-8'), password=None)
        client_pub_key = load_pem_public_key(bytes(body['clientPubKey'], 'utf-8'))
        shared_key = priv_key.exchange(ec.ECDH(), client_pub_key)
        derived_key = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=None,
            info=None,

        ).derive(shared_key)

        decrypt_key = AESGCM(derived_key)

        nonce = [x.to_bytes(1, byteorder='big', signed=True) for x in body['nonce']]
        nonce = b''.join(nonce)

        try:
            password = decrypt_key.decrypt(nonce, base64.b64decode(body['password']), None)

        except:
            error = ApiError(
                code=Error().InvalidPasswordEncryption,
                reason='Invalid password encryption.'
            ).__dict__

            return jsonify(ErrorResponse(
                error=error).__dict__)

        users = mongo_client.users.find()
        usernames = [user['username'] for user in users]

        if body['username'] in usernames:
            error = ApiError(
                code = Error().InvalidUsername,
                reason = 'This username is already taken.'
            ).__dict__

            return jsonify(ErrorResponse(
                        error = error).__dict__)

        else:
            hashed_pass = bcrypt.hashpw(password, bcrypt.gensalt())

            # new_user = User(
            #     username=body['username'],
            #     password=hashed_pass,
            #     sids='[]'
            # )

            # user_session.add(new_user)
            # user_session.flush()

            new_user = {
                'username': body['username'],
                'password': hashed_pass,
                'sids': '[]'
            }

            mongo_client.users.insert_one(new_user)

            new_user_id = mongo_client.users.find_one({'username': body['username']})['_id']

            f = Image.open(app.static_folder+ '/images/socialify-logo.png')
            f.save(f'{os.path.join(app.config["AVATARS_FOLDER"])}{new_user_id}.png')

            mongo_client.login_keys.delete_one({'pub_key': pub_key_string})

            return jsonify(Response(data={}).__dict__)
        
    else:
        error = ApiError(
            code = Error().InvalidAuthToken,
            reason = 'Your authorization token is not valid.'
        ).__dict__

        return jsonify(ErrorResponse(
                    error = error).__dict__)
