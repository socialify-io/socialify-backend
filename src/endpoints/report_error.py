from datetime import time
from app import app, HTTP_METHODS, route, user_session, error_reports_session
from flask import Flask, render_template, request, jsonify
from db.users_db_declarative import UserBase, User, Device
from db.error_reports_db_declarative import ErrorReport

from base64 import b64decode, b64encode
import bcrypt
from datetime import datetime
import pytz

# models
from models.errors._api_error import ApiError

from models.responses._error_response import ErrorResponse
from models.responses._response import Response

from models.errors.codes._error_codes import Error

auth_token_begin_header = '$begin-reportError$'
auth_token_end_header = '$end-reportError$'

@app.route(f'{route}/reportError', methods=HTTP_METHODS)
async def report_error():
    if request.method != 'POST':
        return render_template('what_are_you_looking_for.html')

    try:
        user_agent = request.headers['User-Agent']
        os = request.headers['OS']
        timestamp = int(request.headers['Timestamp'])
        app_version = request.headers['AppVersion']
        auth_token = request.headers['AuthToken']

        headers = {
            'Content-Type': request.headers['Content-Type'],
            'User-Agent': request.headers['User-Agent'],
            'OS': request.headers['OS'],
            'Timestamp': int(request.headers['Timestamp']),
            'AppVersion': request.headers['AppVersion'],
            'AuthToken': request.headers['AuthToken'],
        }

    except:
        error = ApiError(
            code = Error().InvalidHeaders,
            reason = 'Some required request headers not found.'
        ).__dict__
        
        return jsonify(ErrorResponse(
                    errors = [error]).__dict__)

    auth_token_check = bytes(f'{auth_token_begin_header}.{app_version}+{os}+{user_agent}#{timestamp}#.{auth_token_end_header}', 'utf-8')

    if bcrypt.checkpw(auth_token_check, bytes(auth_token, 'utf-8')):
        body = request.get_json(force=True)

        if 'errorType' in body:
            errorType = body['errorType']
        else:
            errorType = None

        if 'errorContext' in body:
            errorContext = body['errorContext']
        else:
            errorContext = None

        if 'messageTitle' in body:
            messageTitle = body['messageTitle']
        else:
            messageTitle = None

        if 'message' in body:
            message = body['message']
        else:
            message = None

        date = datetime.utcfromtimestamp(timestamp).replace(tzinfo=pytz.utc)

        report = ErrorReport(
                errorType = errorType,
                errorContext = errorContext,
                messageTitle = messageTitle,
                message = message,
                appVersion = app_version,
                os = os,
                deviceIP = request.remote_addr,
                timestamp = date
            )

        error_reports_session.add(report)
        error_reports_session.commit()

        return jsonify(Response(data={}).__dict__)

    else:
        error = ApiError(
            code = Error().InvalidAuthToken,
            reason = 'Your authorization token is not valid.'
        ).__dict__

        return jsonify(ErrorResponse(
                    errors = [error]).__dict__)
