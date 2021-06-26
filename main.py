from flask import Flask, render_template, request, jsonify

app = Flask(__name__, template_folder='templates', static_folder='static')

HTTP_METHODS = ['GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'CONNECT', 'OPTIONS', 'TRACE', 'PATCH']

@app.route('/', methods=HTTP_METHODS)
async def what_are_you_looking_for():
    return render_template('what_are_you_looking_for.html')

"""
@app.route('/admin', methods=HTTP_METHODS)
def admin():
    return render_template('admin.html')
"""

from account import register, login

if __name__ == '__main__':
    app.run(debug=True)