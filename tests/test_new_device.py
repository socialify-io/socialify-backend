import pytest
from flask import url_for
import json

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import route, app

from src.RSA_helper import encrypt_public_key, generate_keys, decrypt_private_key
from Crypto.PublicKey import RSA

import datetime

@pytest.fixture
def client():
    client = app.test_client()

    yield client

key = ""

def test_login_getkey(client):
	resp = client.post(
		f'{route}/getkey'
	)

	json_resp = json.loads(resp.data.decode('utf8'))

	print(json_resp)

	global key

	key = json_resp['data']['pubKey']

	assert resp.status_code == 200
	assert json_resp['success'] == True


def test_new_device(client):
	password = 'test_pass123'

	pub_key = RSA.importKey(key)
	enc_pass = encrypt_public_key(password, pub_key)

	timestamp = int(datetime.datetime.now().timestamp())

	payload = {
		'username': 'TestAccount123',
		'password': enc_pass.decode('utf8'),
		'pubKey': key,
		'deviceName': 'Unit test',
		'timestamp': timestamp,
		'appVersion': '0.1',
		'os': 'iOS 14.6'
	}

	resp = client.post(
		f'{route}/newDevice',
		json=payload
	)

	json_resp = json.loads(resp.data.decode('utf8'))

	print(json_resp)

	assert resp.status_code == 200
	assert json_resp['success'] == True