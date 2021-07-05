from sqlite3.dbapi2 import DatabaseError
from flask import Flask, render_template, request, jsonify

#models
from models.errors._api_error import ApiError

from models.responses._error_response import ErrorResponse
from models.responses._response import Response
from models.errors.codes._error_codes import Error

app = Flask(__name__, template_folder='templates', static_folder='static')

HTTP_METHODS = ['GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'CONNECT', 'OPTIONS', 'TRACE', 'PATCH']

VERSION = 0.1
route = f"/api/v{VERSION}"

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

"""
@app.route('/admin', methods=HTTP_METHODS)
def admin():
    return render_template('admin.html')
"""

from account import register, login

if __name__ == '__main__':
    app.run()