from app import app, socketio, url
import os

if __name__ == '__main__':
    socketio.run(app, url, port=int(os.environ.get('PORT', '81')), debug=True)
