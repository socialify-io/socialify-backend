from get_headers import get_headers
import pytest
import json
import hashlib

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import route, app

from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_PSS
from Crypto.Hash import SHA

@pytest.fixture
def client():
    client = app.test_client()

    yield client

def test_remove_device(client):
    with open("tests/key.pem", "r") as f:
        priv_key_string = f.read()

    priv_key = RSA.importKey(priv_key_string)

    headers = get_headers("removeDevice")

    headers.update({
        'Fingerprint': hashlib.sha1(bytes(priv_key_string, 'utf-8')).hexdigest()})

    payload = {
        'device': {
            'deviceName': 'Unit test',
            'fingerprint': hashlib.sha1(bytes(priv_key_string, 'utf-8')).hexdigest()
        }
    }

    signature_json = {
        'headers': headers,
        'body': payload,
        'timestamp': headers['Timestamp'],
        'authToken': headers['AuthToken'],
        'endpointUrl': f'{route}/removeDevice'
    }

    digest = SHA.new(bytes(json.dumps(signature_json), 'utf-8'))
    signer = PKCS1_PSS.new(priv_key)
    signature = signer.sign(digest).hex()
    headers.update({'Signature': str(signature)})

    resp = client.post(
        f'{route}/removeDevice',
        headers=headers,
        json=payload
    )

    json_resp = json.loads(resp.data.decode('utf8'))

    print(json_resp)

    assert resp.status_code == 200
    assert json_resp['success'] == True
