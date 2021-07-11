import pytest
from flask import url_for
import json
import bcrypt
import hashlib

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import route, app

from src.RSA_helper import encrypt_public_key, generate_keys, decrypt_private_key
from Crypto.PublicKey import RSA

import datetime

@pytest.fixture
def client():
    client = app.test_client()

    yield client

def test_get_devices(client):
    with open ("key.pem", "r") as f:
        pub_key_string = f.read()

    pub_key = RSA.importKey(pub_key_string)

    timestamp = int(datetime.datetime.now().timestamp())

    auth_token_begin_header = '$begin-getDevices$'
    auth_token_end_header = '$end-getDevices$'

    os = 'iOS_14.6'
    app_version = '0.1'
    user_agent = 'Socialify-iOS'

    auth_token = bytes(f'{auth_token_begin_header}.{app_version}+{os}+{user_agent}#{timestamp}#.{auth_token_end_header}', 'utf-8')

    auth_token_hashed = bcrypt.hashpw(auth_token, bcrypt.gensalt())

    headers = {
        'Content-Type': 'applictaion/json',
        'User-Agent': user_agent,
        'OS': os,
        'Timestamp': timestamp,
        'AppVersion': app_version,
        'AuthToken': auth_token_hashed.decode(),
        'Fingerprint': hashlib.sha1(bytes(pub_key_string, 'utf-8')).hexdigest()
    }

    payload = {}

    payload_string = json.dumps(payload)
    payload_hashed = hashlib.sha1(bytes(payload_string, 'utf-8'))
    headers_string = json.dumps(headers)
    headers_hashed = hashlib.sha1(bytes(headers_string, 'utf-8'))

    signature_json = {
        'headers': headers_hashed.hexdigest(),
        'body': payload_hashed.hexdigest(),
        'timestamp': timestamp,
        'authToken': auth_token_hashed.decode(),
        'endpointUrl': f'{route}/getDevices'
    }

    signature_string = json.dumps(signature_json)
    signature = encrypt_public_key(signature_string, pub_key)
    headers.update({'Signature': signature})

    resp = client.post(
        f'{route}/getDevices',
		headers=headers
    )

    json_resp = json.loads(resp.data.decode('utf8'))

    print(json_resp)
 
    assert resp.status_code == 200
    assert json_resp['success'] == True