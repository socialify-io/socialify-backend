import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.helpers.get_headers import get_headers, with_fingerprint, without_fingerprint
from app import socketio, user_session
from db.users_db_declarative import Device

def get_user_id(request):
    headers = get_headers(request, with_fingerprint)
    return user_session.query(Device.userId).filter(Device.fingerprint == headers['Fingerprint']).one()[0]
