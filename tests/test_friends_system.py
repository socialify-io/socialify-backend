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

def test_send_friend_request(client):
    with open("tests/key.pem", "r") as f:
        priv_key_string = f.read()

    with open("tests/id.json", "r") as f:
        ids = json.loads(f.read())

    priv_key = RSA.importKey(priv_key_string)

    headers = get_headers("sendFriendRequest")

    headers.update({
        'UserId': ids["userId"],
        'DeviceId': ids["deviceId"]})

    mapped_signature_json = ""

    mapped_headers = f"Content-Type={headers['Content-Type']}&User-Agent={headers['User-Agent']}&OS={headers['OS']}&Timestamp={headers['Timestamp']}&AppVersion={headers['AppVersion']}&AuthToken={headers['AuthToken']}&UserId={headers['UserId']}&DeviceId={headers['DeviceId']}&"

    body = {
        'userId': 2
    }

    signature_json = {
        'headers': mapped_headers,
        'body': f'{body}',
        'timestamp': str(headers['Timestamp']),
        'authToken': str(headers['AuthToken']),
        'endpointUrl': f'{route}/sendFriendRequest'
    }

    for value in signature_json:
        mapped_signature_json += f'{value}={signature_json[value]}' + '&'

    digest = SHA.new(bytes(mapped_signature_json, 'utf-8'))
    signer = PKCS1_v1_5.new(priv_key)
    signature = base64.b64encode(signer.sign(digest))
    headers.update({'Signature': signature})

    resp = client.post(
        f'{route}/sendFriendRequest',
        headers=headers,
        json=body
    )

    json_resp = json.loads(resp.data.decode('utf8'))

    print(json_resp)

    assert resp.status_code == 200
    assert json_resp['success'] == True

friend_requests = []

def test_fetch_pending_friends_requests(client):
    with open("tests/key2.pem", "r") as f:
        priv_key_string = f.read()

    with open("tests/id2.json", "r") as f:
        ids = json.loads(f.read())

    priv_key = RSA.importKey(priv_key_string)

    headers = get_headers("fetchPendingFriendsRequests")

    headers.update({
        'UserId': ids["userId"],
        'DeviceId': ids["deviceId"]})

    mapped_signature_json = ""

    mapped_headers = f"Content-Type={headers['Content-Type']}&User-Agent={headers['User-Agent']}&OS={headers['OS']}&Timestamp={headers['Timestamp']}&AppVersion={headers['AppVersion']}&AuthToken={headers['AuthToken']}&UserId={headers['UserId']}&DeviceId={headers['DeviceId']}&"

    signature_json = {
        'headers': mapped_headers,
        'body': '{}',
        'timestamp': str(headers['Timestamp']),
        'authToken': str(headers['AuthToken']),
        'endpointUrl': f'{route}/fetchPendingFriendsRequests'
    }

    for value in signature_json:
        mapped_signature_json += f'{value}={signature_json[value]}' + '&'

    digest = SHA.new(bytes(mapped_signature_json, 'utf-8'))
    signer = PKCS1_v1_5.new(priv_key)
    signature = base64.b64encode(signer.sign(digest))
    headers.update({'Signature': signature})

    resp = client.get(
        f'{route}/fetchPendingFriendsRequests',
        headers=headers,
        json={}
    )

    json_resp = json.loads(resp.data.decode('utf8'))

    print(json_resp)

    assert resp.status_code == 200
    assert json_resp['success'] == True

    global friend_requests
    friend_requests = json_resp['data']

def test_accept_friend_request(client):
    with open("tests/key2.pem", "r") as f:
        priv_key_string = f.read()

    with open("tests/id2.json", "r") as f:
        ids = json.loads(f.read())

    priv_key = RSA.importKey(priv_key_string)

    headers = get_headers("acceptFriendRequest")

    headers.update({
        'UserId': ids["userId"],
        'DeviceId': ids["deviceId"]})

    mapped_signature_json = ""

    mapped_headers = f"Content-Type={headers['Content-Type']}&User-Agent={headers['User-Agent']}&OS={headers['OS']}&Timestamp={headers['Timestamp']}&AppVersion={headers['AppVersion']}&AuthToken={headers['AuthToken']}&UserId={headers['UserId']}&DeviceId={headers['DeviceId']}&"

    payload = {
        'requestId': friend_requests[0]['id']
    }

    signature_json = {
        'headers': mapped_headers,
        'body': f'{payload}',
        'timestamp': str(headers['Timestamp']),
        'authToken': str(headers['AuthToken']),
        'endpointUrl': f'{route}/acceptFriendRequest'
    }

    for value in signature_json:
        mapped_signature_json += f'{value}={signature_json[value]}' + '&'

    digest = SHA.new(bytes(mapped_signature_json, 'utf-8'))
    signer = PKCS1_v1_5.new(priv_key)
    signature = base64.b64encode(signer.sign(digest))
    headers.update({'Signature': signature})

    resp = client.post(
        f'{route}/acceptFriendRequest',
        headers=headers,
        json=payload
    )

    json_resp = json.loads(resp.data.decode('utf8'))

    print(json_resp)

    assert resp.status_code == 200
    assert json_resp['success'] == True

def test_fetch_friends(client):
    headers = get_headers("fetchFriends")

    payload = {
        'userId': 2
    }

    resp = client.get(
        f'{route}/fetchFriends',
        headers=headers,
        json=payload
    )

    json_resp = json.loads(resp.data.decode('utf8'))

    print(json_resp)

    assert resp.status_code == 200
    assert json_resp['success'] == True


def test_get_mutual_friends(client):
    headers = get_headers("getMutualFriends")

    payload = {
        'users': [1, 2]
    }

    resp = client.get(
        f'{route}/getMutualFriends',
        headers=headers,
        json=payload
    )

    json_resp = json.loads(resp.data.decode('utf8'))

    print(json_resp)

    assert resp.status_code == 200
    assert json_resp['success'] == False

def test_remove_friend(client):
    with open("tests/key.pem", "r") as f:
        priv_key_string = f.read()

    with open("tests/id.json", "r") as f:
        ids = json.loads(f.read())

    priv_key = RSA.importKey(priv_key_string)

    headers = get_headers("removeFriend")

    headers.update({
        'UserId': ids["userId"],
        'DeviceId': ids["deviceId"]})

    mapped_signature_json = ""

    mapped_headers = f"Content-Type={headers['Content-Type']}&User-Agent={headers['User-Agent']}&OS={headers['OS']}&Timestamp={headers['Timestamp']}&AppVersion={headers['AppVersion']}&AuthToken={headers['AuthToken']}&UserId={headers['UserId']}&DeviceId={headers['DeviceId']}&"

    payload = {
        'userId': 2
    }

    signature_json = {
        'headers': mapped_headers,
        'body': f'{payload}',
        'timestamp': str(headers['Timestamp']),
        'authToken': str(headers['AuthToken']),
        'endpointUrl': f'{route}/removeFriend'
    }

    for value in signature_json:
        mapped_signature_json += f'{value}={signature_json[value]}' + '&'

    digest = SHA.new(bytes(mapped_signature_json, 'utf-8'))
    signer = PKCS1_v1_5.new(priv_key)
    signature = base64.b64encode(signer.sign(digest))
    headers.update({'Signature': signature})

    resp = client.post(
        f'{route}/removeFriend',
        headers=headers,
        json=payload
    )

    json_resp = json.loads(resp.data.decode('utf8'))

    print(json_resp)

    assert resp.status_code == 200
    assert json_resp['success'] == True

