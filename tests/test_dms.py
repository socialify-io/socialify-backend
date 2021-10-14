import sys
import os
import json
import base64

from get_headers import get_headers

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import route, app, socketio

from Crypto.PublicKey import RSA
from Crypto.Hash import SHA
from Crypto.Signature import PKCS1_v1_5
import hashlib

client = ''
client2 = ''

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

    global client
    client = socketio.test_client(app, headers=headers)

    assert client.is_connected()

def test_send_dm():
    client.emit('find_user', 'TestAcco')
    receiver_id = client.get_received()[1]['args'][0][0]['id']

    client.emit('send_dm', {
        'receiverId': receiver_id,
        'message': 'Test message'
        })

    response = client.get_received()[0]['args'][0]

    assert response['message'] == 'Test message'
    assert response['username'] == 'TestAccount123'

def test_connect_client2():
    with open("tests/key2.pem", "r") as f:
        priv_key_string = f.read()

    with open("tests/id2.txt", "r") as f:
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

    global client2
    client2 = socketio.test_client(app, headers=headers)

    assert client2.is_connected()

def test_fetch_last_unread_dms():
    client2.emit('fetch_last_unread_dms')
    response = client2.get_received()[1]['args'][0][0]

    assert response['sender'] == 1
    assert response['receiver'] == 2
    assert response['message'] == 'Test message'
