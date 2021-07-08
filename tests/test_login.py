import pytest
from flask import url_for
import json

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import route, app

from account.pass_enc import encrypt_public_key, generate_keys, decrypt_private_key
from Crypto.PublicKey import RSA

@pytest.fixture
def client():
    client = app.test_client()

    yield client

register_key = ""
login_key = ""

def test_register_getkey(client):
	resp = client.post(
		f'{route}/getkey'
	)

	json_resp = json.loads(resp.data.decode('utf8'))

	print(json_resp)

	global register_key

	register_key = json_resp['data']['pubKey']

	assert resp.status_code == 200
	assert json_resp['success'] == True

def test_register(client):
	password = 'test_pass123'

	pub_key = RSA.importKey(register_key)
	enc_pass = encrypt_public_key(password, pub_key)

	payload = {
		'username': 'TestAccount123',
		'password': enc_pass.decode('utf8'),
		'repeat_password': enc_pass.decode('utf8'),
		'pubKey': register_key
	}

	resp = client.post(
		f'{route}/register',
		json=payload
	)

	json_resp = json.loads(resp.data.decode('utf8'))

	print(json_resp)

	assert resp.status_code == 200
	assert json_resp['success'] == True

def test_login_getkey(client):
	resp = client.post(
		f'{route}/getkey'
	)

	json_resp = json.loads(resp.data.decode('utf8'))

	print(json_resp)

	global login_key

	login_key = json_resp['data']['pubKey']

	assert resp.status_code == 200
	assert json_resp['success'] == True


def test_login(client):
	password = 'test_pass123'

	pub_key = RSA.importKey(login_key)
	enc_pass = encrypt_public_key(password, pub_key)

	payload = {
		'username': 'TestAccount123',
		'password': enc_pass.decode('utf8'),
		'pubKey': login_key
	}

	resp = client.post(
		f'{route}/login',
		json=payload
	)

	json_resp = json.loads(resp.data.decode('utf8'))

	print(json_resp)

	assert resp.status_code == 200
	assert json_resp['success'] == True