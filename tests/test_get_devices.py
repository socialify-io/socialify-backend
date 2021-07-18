import pytest
from flask import url_for
import json
import bcrypt
import hashlib
from Crypto.Signature import PKCS1_PSS

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import route, app

from src.helpers.RSA_helper import encrypt_rsa, generate_keys, decrypt_rsa
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Hash import SHA

import datetime


@pytest.fixture
def client():
    client = app.test_client()

    yield client


def test_get_devices(client):
    with open("tests/key.pem", "r") as f:
        priv_key_string = f.read()

    priv_key = RSA.importKey(priv_key_string)

    timestamp = int(datetime.datetime.now().timestamp())

    auth_token_begin_header = '$begin-getDevices$'
    auth_token_end_header = '$end-getDevices$'

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
        'AuthToken': auth_token_hashed.decode(),
        'Fingerprint': hashlib.sha1(bytes(priv_key_string, 'utf-8')).hexdigest()
    }

    payload = {}

    signature_json = {
        'headers': headers,
        'body': payload,
        'timestamp': timestamp,
        'authToken': auth_token_hashed.decode(),
        'endpointUrl': f'{route}/getDevices'
    }

    digest = SHA.new(bytes(json.dumps(signature_json), 'utf-8'))
    signer = PKCS1_PSS.new(priv_key)
    signature = signer.sign(digest).hex()
    print(digest)
    headers.update({'Signature': str(signature)})

    # print(headers)

    resp = client.post(
        f'{route}/getDevices',
        headers=headers
    )

    json_resp = json.loads(resp.data.decode('utf8'))

    print(json_resp)

    assert resp.status_code == 200
    assert json_resp['success'] == True