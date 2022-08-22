from get_headers import get_headers
from get_key import get_key
import pytest
import json
import hashlib

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import route, app

from src.helpers.RSA_helper import encrypt_rsa, generate_keys
from Crypto.PublicKey import RSA

@pytest.fixture
def client():
    client = app.test_client()

    yield client

def test_new_device(client):
    key = get_key(client)
    pem_prefix = '-----BEGIN RSA PRIVATE KEY-----\n'
    pem_suffix = '\n-----END RSA PRIVATE KEY-----'
    key_with_fixes = '{}{}{}'.format(pem_prefix, key, pem_suffix)

    password = 'test_pass123'

    pub_key = RSA.importKey(key_with_fixes)
    enc_pass = encrypt_rsa(password, pub_key)

    headers = get_headers("newDevice")

    keys = generate_keys()
    priv_key = keys.exportKey().decode('utf-8')
    pub_key = keys.publickey().exportKey().decode('utf-8')

    payload = {
        'username': 'TestAccount123',
        'password': enc_pass.decode('utf8'),
        'pubKey': key,
        'device': {
            'deviceName': 'Unit test',
            'signPubKey': pub_key
                .replace('-----BEGIN PUBLIC KEY-----\n', '')
                .replace('\n-----END PUBLIC KEY-----', '')
        }
    }

    resp = client.post(
        f'{route}/newDevice',
        headers=headers,
        json=payload
    )

    json_resp = json.loads(resp.data.decode('utf8'))
    print(json_resp)

    f = open("tests/key.pem", "w")
    f.write(str(priv_key))
    f.close()

    f = open("tests/id.json", "w")
    json.dump(json_resp["data"], f)
    f.close()

    assert resp.status_code == 200
    assert json_resp['success'] == True

def test_new_device_2(client):
    key = get_key(client)
    pem_prefix = '-----BEGIN RSA PRIVATE KEY-----\n'
    pem_suffix = '\n-----END RSA PRIVATE KEY-----'
    key_with_fixes = '{}{}{}'.format(pem_prefix, key, pem_suffix)

    password = 'test_pass123'

    pub_key = RSA.importKey(key_with_fixes)
    enc_pass = encrypt_rsa(password, pub_key)

    headers = get_headers("newDevice")

    keys = generate_keys()
    priv_key = keys.exportKey().decode('utf-8')
    pub_key = keys.publickey().exportKey().decode('utf-8')

    payload = {
        'username': 'TestAccountSecondary',
        'password': enc_pass.decode('utf8'),
        'pubKey': key,
        'device': {
            'deviceName': 'Unit test',
            'signPubKey': pub_key
                .replace('-----BEGIN PUBLIC KEY-----\n', '')
                .replace('\n-----END PUBLIC KEY-----', '')
        }
    }

    resp = client.post(
        f'{route}/newDevice',
        headers=headers,
        json=payload
    )

    json_resp = json.loads(resp.data.decode('utf8'))
    print(json_resp)

    f = open("tests/key2.pem", "w")
    f.write(str(priv_key))
    f.close()

    f = open("tests/id2.json", "w")
    json.dump(json_resp["data"], f)
    f.close()

    assert resp.status_code == 200
    assert json_resp['success'] == True

