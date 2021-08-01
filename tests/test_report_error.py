from get_headers import get_headers
import pytest
import json

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import route, app

@pytest.fixture
def client():
    client = app.test_client()

    yield client

def test_report_error(client):
    headers = get_headers("reportError")

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
