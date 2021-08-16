from app import app, socketio
import os

if __name__ == '__main__':
    socketio.run(app, port=int(os.environ.get('PORT', '80')))