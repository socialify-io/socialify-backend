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

    with open("tests/id.json", "r") as f:
        ids = json.loads(f.read())

    priv_key = RSA.importKey(priv_key_string)

    headers = get_headers('connect')

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

def test_connect_client2():
    with open("tests/key2.pem", "r") as f:
        priv_key_string = f.read()

    with open("tests/id2.json", "r") as f:
        ids = json.loads(f.read())

    priv_key = RSA.importKey(priv_key_string)

    headers = get_headers('connect')

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

def test_create_room():
    client.emit('create_room', {'roomName': 'test_room'})
    response = client.get_received()[0]['args'][0]
    print(response)

    assert response['success'] == True

def test_join_room():
    client2.emit('join_to_room', {'roomId': 1})
    response = client2.get_received()[0]['args'][0]
    print(response)

    assert response['success'] == True

def test_send_message():
    client.emit('send_message', {'roomId': 1, 'message': 'test_message'})
    response = client.get_received()[0]['args'][0]
    print(response)

    assert response['message'] == 'test_message'

