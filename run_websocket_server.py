from app import app, socketio
import os

if __name__ == '__main__':
    socketio.run(app, '192.168.8.199', port=int(os.environ.get('PORT', '81')), debug=True)
