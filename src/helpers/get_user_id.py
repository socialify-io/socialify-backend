import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.helpers.get_headers import get_headers, with_device_id, without_device_id
from app import socketio, mongo_client

def get_user_id(request):
    headers = get_headers(request, with_device_id)
    #return user_session.query(Device.userId).filter(Device.fingerprint == headers['Fingerprint']).one()[0]
    return mongo_client.devices.find_one({"fingerprint": headers['Fingerprint']})["userId"]