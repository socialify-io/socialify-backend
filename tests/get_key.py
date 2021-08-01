import json
from get_headers import get_headers

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import route

def get_key(client):
    headers = get_headers("getKey")

    resp = client.post(
        f'{route}/getKey',
        headers=headers
    )

    json_resp = json.loads(resp.data.decode('utf8'))

    print(json_resp)

    return json_resp['data']['pubKey']