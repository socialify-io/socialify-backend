import pytest
import json
from get_headers import get_headers
from get_key import get_key

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import route, app

from src.helpers.RSA_helper import encrypt_rsa
from Crypto.PublicKey import RSA


@pytest.fixture
def client():
    client = app.test_client()

    yield client

def test_register(client):
    key = get_key(client)
    pem_prefix = '-----BEGIN RSA PRIVATE KEY-----\n'
    pem_suffix = '\n-----END RSA PRIVATE KEY-----'
    key_with_fixes = '{}{}{}'.format(pem_prefix, key, pem_suffix)

    password = 'test_pass123'

    pub_key = RSA.importKey(key_with_fixes)
    enc_pass = encrypt_rsa(password, pub_key)

    headers = get_headers("register")

    payload = {
        'username': 'TestAccount123',
        'password': enc_pass.decode('utf8'),
        'repeat_password': enc_pass.decode('utf8'),
        'pubKey': key
    }

    resp = client.post(
        f'{route}/register',
        headers=headers,
        json=payload
    )

    json_resp = json.loads(resp.data.decode('utf8'))

    assert resp.status_code == 200
    assert json_resp['success'] == True


def test_register_second_account(client):
    key = get_key(client)
    pem_prefix = '-----BEGIN RSA PRIVATE KEY-----\n'
    pem_suffix = '\n-----END RSA PRIVATE KEY-----'
    key_with_fixes = '{}{}{}'.format(pem_prefix, key, pem_suffix)

    password = 'test_pass123'

    pub_key = RSA.importKey(key_with_fixes)
    enc_pass = encrypt_rsa(password, pub_key)

    headers = get_headers("register")

    payload = {
        'username': 'TestAccountSecondary',
        'password': enc_pass.decode('utf8'),
        'repeat_password': enc_pass.decode('utf8'),
        'pubKey': key
    }

    resp = client.post(
        f'{route}/register',
        headers=headers,
        json=payload
    )

    json_resp = json.loads(resp.data.decode('utf8'))

    print(json_resp)

    assert resp.status_code == 200
    assert json_resp['success'] == True
