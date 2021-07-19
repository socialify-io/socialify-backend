import pytest
from flask import url_for
import json
import bcrypt
import hashlib

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import route, app

from src.helpers.RSA_helper import encrypt_rsa, generate_keys, decrypt_rsa
from Crypto.PublicKey import RSA

import datetime


@pytest.fixture
def client():
    client = app.test_client()

    yield client

def test_remove_device(client):

    timestamp = int(datetime.datetime.now().timestamp())

    auth_token_begin_header = '$begin-removeDevice$'
    auth_token_end_header = '$end-removeDevice$'

    os = 'iOS_14.6'
    app_version = '0.1'
    user_agent = 'Socialify-iOS'

    auth_token = bytes(
        f'{auth_token_begin_header}.{app_version}+{os}+{user_agent}#{timestamp}#.{auth_token_end_header}', 'utf-8')

    auth_token_hashed = bcrypt.hashpw(auth_token, bcrypt.gensalt())

    headers = {
        'Content-Type': 'applictaion/json',
        'User-Agent': user_agent,
        'OS': os,
        'Timestamp': timestamp,
        'AppVersion': app_version,
        'AuthToken': auth_token_hashed
    }

    #keys = generate_keys()
    #priv_key = keys.exportKey().decode('utf-8')
    # pub_key = keys.publickey().exportKey().decode('utf-8')

    payload = {
        'device': {
            'deviceName': 'Unit test',
            'fingerprint': '5f3c827876d88ef1358e38addd43ef4a6855c52d'
        }
    }

    resp = client.post(
        f'{route}/removeDevice',
        headers=headers,
        json=payload
    )

    json_resp = json.loads(resp.data.decode('utf8'))

    print(json_resp)

    #f = open("tests/key.pem", "w")
    #f.write(str(priv_key))
    #f.close()

    assert resp.status_code == 200
    assert json_resp['success'] == True
