import sys
import os
import json

from get_headers import get_headers

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import route, app, socketio

from Crypto.PublicKey import RSA
from Crypto.Hash import SHA
from Crypto.Signature import PKCS1_PSS
import hashlib

def test_send_message():
    with open("tests/key.pem", "r") as f:
        priv_key_string = f.read()

    priv_key = RSA.importKey(priv_key_string)

    headers = get_headers("connect")

    headers.update({
        'Fingerprint': hashlib.sha1(bytes(priv_key_string, 'utf-8')).hexdigest()})

    signature_json = {
        'headers': headers,
        'body': {},
        'timestamp': headers['Timestamp'],
        'authToken': headers['AuthToken'],
        'endpointUrl': f'{route}/connect'
    }

    digest = SHA.new(bytes(json.dumps(signature_json), 'utf-8'))
    signer = PKCS1_PSS.new(priv_key)
    signature = signer.sign(digest).hex()
    headers.update({'Signature': signature})

    client = socketio.test_client(app, headers=headers)
    print(client.get_received())
    assert client.is_connected()