import pytest
from flask import url_for
import json
import bcrypt
import hashlib

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import route, app

from src.helpers.RSA_helper import encrypt_rsa, generate_keys, decrypt_rsa
from Crypto.PublicKey import RSA

import datetime

@pytest.fixture
def client():
	client = app.test_client()

	yield client

key = ""

def test_login_getkey(client):
	timestamp = int(datetime.datetime.now().timestamp())

	auth_token_begin_header = '$begin-getKey$'
	auth_token_end_header = '$end-getKey$'

	os = 'iOS_14.6'
	app_version = '0.1'
	user_agent = 'Socialify-iOS'

	auth_token = bytes(f'{auth_token_begin_header}.{app_version}+{os}+{user_agent}#{timestamp}#.{auth_token_end_header}', 'utf-8')

	auth_token_hashed = bcrypt.hashpw(auth_token, bcrypt.gensalt())

	headers = {
		'Content-Type': 'applictaion/json',
		'User-Agent': user_agent,
		'OS': os,
		'Timestamp': timestamp,
		'AppVersion': app_version,
		'AuthToken': auth_token_hashed
	}

	resp = client.post(
		f'{route}/getKey',
		headers=headers
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
	enc_pass = encrypt_rsa(password, pub_key)

	timestamp = int(datetime.datetime.now().timestamp())

	auth_token_begin_header = '$begin-newDevice$'
	auth_token_end_header = '$end-newDevice$'

	os = 'iOS_14.6'
	app_version = '0.1'
	user_agent = 'Socialify-iOS'

	auth_token = bytes(f'{auth_token_begin_header}.{app_version}+{os}+{user_agent}#{timestamp}#.{auth_token_end_header}', 'utf-8')

	auth_token_hashed = bcrypt.hashpw(auth_token, bcrypt.gensalt())
	
	headers = {
		'Content-Type': 'applictaion/json',
		'User-Agent': user_agent,
		'OS': os,
		'Timestamp': timestamp,
		'AppVersion': app_version,
		'AuthToken': auth_token_hashed
	}

	keys = generate_keys()
	priv_key = keys.exportKey().decode('utf-8')
	pub_key = keys.publickey().exportKey().decode('utf-8')

	payload = {
		'username': 'TestAccount123',
		'password': enc_pass.decode('utf8'),
		'pubKey': key,
		'device': {
			'deviceName': 'Unit test',
			'timestamp': timestamp,
			'appVersion': '0.1',
			'os': 'iOS 14.6',
			'signPubKey': pub_key,
			'fingerprint': hashlib.sha1(bytes(priv_key, 'utf-8')).hexdigest()
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

	assert resp.status_code == 200
	assert json_resp['success'] == True