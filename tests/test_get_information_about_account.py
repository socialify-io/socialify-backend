import pytest
import json
from get_headers import get_headers
from Crypto.Signature import PKCS1_v1_5
import hashlib
import base64

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import route, app, socketio

from Crypto.PublicKey import RSA
from Crypto.Hash import SHA
from Crypto.Signature import PKCS1_v1_5

@pytest.fixture
def client():
    client = app.test_client()

    yield client

def test_get_information_about_account_http(client):
    headers = get_headers('getInformationAboutAccount')
    resp = client.post(
        f'{route}/getInformationAboutAccount',
        headers=headers,
        json={"userId": 1}
    )

    json_resp = json.loads(resp.data.decode())

    print(json_resp)

    assert resp.status_code == 200
    assert json_resp['data']['username'] == 'TestAccount123'

message_token = ''
websocket_client = ''

def test_connect():
    with open("tests/key.pem", "r") as f:
        priv_key_string = f.read()

    with open("tests/id.txt", "r") as f:
        id = f.read()

    priv_key = RSA.importKey(priv_key_string)

    headers = get_headers('connect')

    headers.update({
        'Fingerprint': hashlib.sha1(bytes(priv_key_string, 'utf-8')).hexdigest(),
        'DeviceId': id})

    mapped_headers = ""
    mapped_signature_json = ""

    for value in headers:
        mapped_headers += f'{value}={headers[value]}' + '&'

    signature_json = {
        'headers': mapped_headers,
        'body': '{}',
        'timestamp': str(headers['Timestamp']),
        'authToken': str(headers['AuthToken']),
        'endpointUrl': f'{route}/connect'
    }

    for value in signature_json:
        mapped_signature_json += f'{value}={signature_json[value]}' + '&'

    digest = SHA.new(bytes(mapped_signature_json, 'utf-8'))
    signer = PKCS1_v1_5.new(priv_key)
    signature = base64.b64encode(signer.sign(digest))
    headers.update({'Signature': signature})

    print(signature)

    global websocket_client
    websocket_client = socketio.test_client(app, headers=headers)

    global message_token
    message_token = websocket_client.get_received()[0]['args'][0]['data']['messageToken']

    assert websocket_client.is_connected()

def test_get_information_about_account():
    websocket_client.emit('get_information_about_account', 1)
    response = websocket_client.get_received()[0]['args'][0]

    assert response['username'] == 'TestAccount123'
