from app import app, socketio
import os

if __name__ == '__main__':
    socketio.run(app, '192.168.8.151', port=int(os.environ.get('PORT', '82')), debug=True)
