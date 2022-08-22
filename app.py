from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO
import logging
import datetime

# Models
from models.errors._api_error import ApiError

from models.responses._error_response import ErrorResponse
from models.errors.codes._error_codes import Error

app = Flask(__name__, template_folder='templates', static_folder='static')

MAX_BUFFER_SIZE = 50 * 1000 * 1000
socketio = SocketIO(app, logger=False, engineio_logger=False, policy_server=False, manage_session=False, cors_allowed_origins="*", max_http_buffer_size=MAX_BUFFER_SIZE)

HTTP_METHODS = ['GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'CONNECT', 'OPTIONS', 'TRACE', 'PATCH']

AVATARS_FOLDER = 'static/avatars/'
GROUPS_ICONS_FOLDER = 'static/groups_icons/'
MEDIA_FOLDER = 'static/media/'

app.config['AVATARS_FOLDER'] = AVATARS_FOLDER
app.config['MEDIA_FOLDER'] = MEDIA_FOLDER
app.config['GROUPS_ICONS_FOLDER'] = GROUPS_ICONS_FOLDER

VERSION = 0.1
route = f"/api/v{VERSION}"
url = '192.168.8.199'

logging.basicConfig(filename=f'./logs/logs.log', level=logging.DEBUG, format=f'%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')

from pymongo import MongoClient

CONNECTION_STRING = "mongodb://localhost/socialify"
mongo_client = MongoClient(CONNECTION_STRING)['socialify']


@app.errorhandler(400)
def bad_request(e):
    error = ApiError(
        code=Error().BadRequest,
        reason=f'{str(e)}'
    ).__dict__

    return jsonify(ErrorResponse(
        error=error).__dict__)

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
        error=error).__dict__)

@app.after_request
def add_header(response):
    response.headers['Server'] = 'Socialify/0.1'
    return response

# Endpoints
from src.endpoints import get_information_about_account#, get_information_about_account_http
from src.endpoints.friends import send_friend_request, fetch_pending_friends_requests, accept_friend_request, fetch_friends, remove_friend, get_mutual_friends
from src.endpoints.account import get_key, register, get_devices, edit_account
from src.endpoints.account import new_device
from src.endpoints.account import remove_device
from src.endpoints.account import report_error

from src.endpoints.messages import connect, find_user, dm, groups, disconnect
