from flask import Flask, render_template, request, jsonify

from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import base64

app = Flask(__name__, template_folder='templates', static_folder='static')

HTTP_METHODS = ['GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'CONNECT', 'OPTIONS', 'TRACE', 'PATCH']

VERSION = 0.1
route = f"/api/v{VERSION}"

@app.errorhandler(404)
def page_not_found(e):
    return render_template('what_are_you_looking_for.html')

"""
@app.route('/admin', methods=HTTP_METHODS)
def admin():
    return render_template('admin.html')
"""

from account import register, login

if __name__ == '__main__':
    app.run(debug=True)