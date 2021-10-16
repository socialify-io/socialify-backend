from get_headers import get_headers
import pytest
import json
import hashlib
import base64

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import route, app

from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA

@pytest.fixture
def client():
    client = app.test_client()

    yield client

def test_upload_avatar(client):
    with open('tests/key.pem', 'r') as f:
        priv_key_string = f.read()

    with open('tests/id.txt', 'r') as f:
        id = f.read()

    priv_key = RSA.importKey(priv_key_string)

    headers = get_headers('uploadAvatar')
    headers.update({
        'Fingerprint': hashlib.sha1(bytes(priv_key_string, 'utf-8')).hexdigest(),
        'DeviceId': id})

    mapped_headers = ""
    mapped_signature_json = ""

    for value in headers:
        mapped_headers += f'{value}={headers[value]}' + '&'

    payload = {
        'avatar': base64.b64encode(open(app.static_folder+ '/images/socialify-logo.png', 'rb').read()).decode()
    }

    signature_json = {
        'headers': mapped_headers,
        'body': f'{payload}',
        'timestamp': str(headers['Timestamp']),
        'authToken': str(headers['AuthToken']),
        'endpointUrl': f'{route}/uploadAvatar'
    }

    for value in signature_json:
        mapped_signature_json += f'{value}={signature_json[value]}' + '&'

    digest = SHA.new(bytes(mapped_signature_json, 'utf-8'))
    signer = PKCS1_v1_5.new(priv_key)
    signature = base64.b64encode(signer.sign(digest))
    headers.update({'Signature': signature})

    resp = client.post(
        f'{route}/uploadAvatar',
        headers=headers,
        json=payload
    )

    json_resp = json.loads(resp.data.decode('utf8'))

    print(json_resp)

    assert resp.status_code == 200
    assert json_resp['success'] == True

def test_get_avatar(client):
    resp = client.get(
    f'{route}/getAvatar/1')

    assert resp.status_code == 301
