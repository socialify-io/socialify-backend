from app import app, HTTP_METHODS, route, mongo_client
from flask import render_template, request, jsonify

# Database
# from db.users_db_declarative import LoginKey

# Helpers
from ...helpers.RSA_helper import generate_keys
from ...helpers.get_headers import get_headers, with_device_id, without_device_id
from ...helpers.verify_authtoken import verify_authtoken

# Models
from models.errors._api_error import ApiError

from models.responses._error_response import ErrorResponse
from models.responses._response import Response

from models.errors.codes._error_codes import Error

#Crypto
from Crypto.PublicKey import ECC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from  cryptography.hazmat.primitives.serialization import Encoding, PrivateFormat, PublicFormat, BestAvailableEncryption, KeySerializationEncryption, NoEncryption

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
#        key = ECC.generate(curve='P-256')
#
#        private_key = key.export_key(format='PEM')
#        public_key = key.public_key().export_key(format='PEM')
#
#        clear_public_key =  public_key.replace('\n', '').replace('-----BEGIN PUBLIC KEY-----', '').replace('-----END PUBLIC KEY-----', '')

        key = ec.generate_private_key(ec.SECP256R1())

        pub_key = key.public_key().public_bytes(encoding=Encoding.PEM, format=PublicFormat.SubjectPublicKeyInfo).decode()
        priv_key = key.private_bytes(encoding=Encoding.PEM, format=PrivateFormat.PKCS8, encryption_algorithm=NoEncryption()).decode()

        # new_key = LoginKey(
        #     pub_key = pub_key,
        #     priv_key = priv_key
        # )

        # key_session.add(new_key)
        # key_session.commit()

        new_key = {
            'pub_key': pub_key,
            'priv_key': priv_key
        }

        mongo_client.login_keys.insert_one(new_key)

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
                    error = error).__dict__)

def compress_point(point):
    return hex(point.x) + hex(point.y % 2)[2:]
