import pytest
from flask import url_for
import json
import hashlib
import datetime
import bcrypt

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import route, app

@pytest.fixture
def client():
    client = app.test_client()

    yield client

def test_report_error(client):
    timestamp = int(datetime.datetime.now().timestamp())

    auth_token_begin_header = '$begin-reportError$'
    auth_token_end_header = '$end-reportError$'

    os = 'iOS_14.6'
    app_version = '0.1'
    user_agent = 'Socialify-iOS'

    auth_token = bytes(f'{auth_token_begin_header}.{app_version}+{os}+{user_agent}#{timestamp}#.{auth_token_end_header}', 'utf-8')

    auth_token_hashed = bcrypt.hashpw(auth_token, bcrypt.gensalt())

    headers = {
        'Content-Type': 'application/json',
        'User-Agent': user_agent,
        'OS': os,
        'Timestamp': timestamp,
        'AppVersion': app_version,
        'AuthToken': auth_token_hashed
    }

    payload = {
        'errorType': 'ApiError.InvalidAuthToken',
        'errorContext': 'Invalid auth token on registering account in getKey.swift',
        'message': 'Hi, I get an error when I trying to register an account.',
    }

    resp = client.post(
        f'{route}/reportError',
        headers=headers,
        json=payload
    )

    json_resp = json.loads(resp.data.decode('utf8'))

    print(json_resp)

    assert resp.status_code == 200
    assert json_resp['success'] == True
