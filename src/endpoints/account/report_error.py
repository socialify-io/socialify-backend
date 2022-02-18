from app import app, HTTP_METHODS, route, error_reports_session
from flask import render_template, request, jsonify

# Database
from db.error_reports_db_declarative import ErrorReport

# Helpers
from ...helpers.get_headers import get_headers, with_device_id, without_device_id
from ...helpers.verify_authtoken import verify_authtoken

# Datatime
from datetime import datetime
import pytz

# Models
from models.errors._api_error import ApiError

from models.responses._error_response import ErrorResponse
from models.responses._response import Response

from models.errors.codes._error_codes import Error


@app.route(f'{route}/reportError', methods=['POST'])
async def report_error():
    try:
        headers = get_headers(request, without_device_id)

    except:
        error = ApiError(
            code = Error().InvalidHeaders,
            reason = 'Some required request headers not found.'
        ).__dict__

        return jsonify(ErrorResponse(
                    error=error).__dict__)

    if verify_authtoken(headers, "reportError"):
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

        date = datetime.utcfromtimestamp(headers["Timestamp"]).replace(tzinfo=pytz.utc)

        report = ErrorReport(
                errorType = errorType,
                errorContext = errorContext,
                messageTitle = messageTitle,
                message = message,
                appVersion = headers["AppVersion"],
                os = headers["OS"],
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
                    error=error).__dict__)

