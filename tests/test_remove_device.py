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

def test_remove_device(client):
    with open('tests/key.pem', 'r') as f:
        priv_key_string = f.read()

    with open('tests/id.json', 'r') as f:
        ids = json.loads(f.read())

    priv_key = RSA.importKey(priv_key_string)

    headers = get_headers('removeDevice')
    headers.update({
        'UserId': ids['userId'],
        'DeviceId': ids['deviceId']})

    mapped_signature_json = ""

    mapped_headers = f"Content-Type={headers['Content-Type']}&User-Agent={headers['User-Agent']}&OS={headers['OS']}&Timestamp={headers['Timestamp']}&AppVersion={headers['AppVersion']}&AuthToken={headers['AuthToken']}&UserId={headers['UserId']}&DeviceId={headers['DeviceId']}&"

    signature_json = {
        'headers': mapped_headers,
        'body': '{}',
        'timestamp': str(headers['Timestamp']),
        'authToken': str(headers['AuthToken']),
        'endpointUrl': f'{route}/removeDevice'
    }

    for value in signature_json:
        mapped_signature_json += f'{value}={signature_json[value]}' + '&'

    digest = SHA.new(bytes(mapped_signature_json, 'utf-8'))
    signer = PKCS1_v1_5.new(priv_key)
    signature = base64.b64encode(signer.sign(digest))
    headers.update({'Signature': signature})

    resp = client.post(
        f'{route}/removeDevice',
        headers=headers,
        json={}
    )

    json_resp = json.loads(resp.data.decode('utf8'))

    print(json_resp)

    assert resp.status_code == 200
    assert json_resp['success'] == True
