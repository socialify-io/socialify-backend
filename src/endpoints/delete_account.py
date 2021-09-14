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


@app.route(f'{route}/deleteAccount', methods=HTTP_METHODS)
async def register():
    if request.method != 'POST':
        return render_template('what_are_you_looking_for.html')
    
    try:
        headers = get_headers(request, with_fingerprint)

    except:
        error = ApiError(
            code = Error().InvalidHeaders,
            reason = 'Some required request headers not found.'
        ).__dict__
        
        return jsonify(ErrorResponse(
                    errors = [error]).__dict__)

    if verify_authtoken(headers, "deleteAccount"):
