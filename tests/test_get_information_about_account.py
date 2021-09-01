import pytest
import json
from get_headers import get_headers
from Crypto.Signature import PKCS1_v1_5
import hashlib
import base64

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import route, app

from Crypto.PublicKey import RSA
from Crypto.Hash import SHA

@pytest.fixture
def client():
    client = app.test_client()

    yield client


def test_get_information_about_account(client):
    headers = get_headers('getInformationAboutAccount')
    resp = client.post(
        f'{route}/getInformationAboutAccount',
        headers=headers,
        json={"userId": 0}
    )
