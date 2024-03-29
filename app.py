from flask import Flask, render_template, jsonify

# Models
from models.errors._api_error import ApiError

from models.responses._error_response import ErrorResponse
from models.errors.codes._error_codes import Error

app = Flask(__name__, template_folder='templates', static_folder='static')

HTTP_METHODS = ['GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'CONNECT', 'OPTIONS', 'TRACE', 'PATCH']

VERSION = 0.1
route = f"/api/v{VERSION}"

# Database
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
 
from db.keys_db_declarative import KeyBase
from db.users_db_declarative import UserBase
from db.error_reports_db_declarative import ErrorReportsBase

key_engine = create_engine('sqlite:///db/keys.db', connect_args={'check_same_thread': False})
KeyBase.metadata.bind = key_engine
 
key_DBSession = sessionmaker(bind=key_engine)
key_session = key_DBSession()


user_engine = create_engine('sqlite:///db/users.db', connect_args={'check_same_thread': False})
UserBase.metadata.bind = user_engine
 
user_DBSession = sessionmaker(bind=user_engine)
user_session = user_DBSession()


error_reports_engine = create_engine('sqlite:///db/error_reports.db', connect_args={'check_same_thread': False})
ErrorReportsBase.metadata.bind = error_reports_engine
 
error_reports_DBSession = sessionmaker(bind=error_reports_engine)
error_reports_session = error_reports_DBSession()

@app.errorhandler(400)
def bad_request(e):
    error = ApiError(
        code=Error().BadRequest,
        reason=f'{str(e)}'
    ).__dict__

    return jsonify(ErrorResponse(
        errors=[error]).__dict__)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('what_are_you_looking_for.html')

@app.errorhandler(500)
def internal_server_error(e):
    error = ApiError(
        code=Error().InternalServerError,
        reason=f'{str(e)}'
    ).__dict__

    return jsonify(ErrorResponse(
        errors=[error]).__dict__)

@app.after_request
def add_header(response):
    response.headers['Server'] = 'Socialify/0.1'
    return response

# Endpoints
from src.endpoints import get_key, register, get_devices
from src.endpoints import new_device
from src.endpoints import remove_device
from src.endpoints import report_error

if __name__ == '__main__':
    app.run()
