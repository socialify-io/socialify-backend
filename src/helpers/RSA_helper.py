from app import route
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import base64
from Crypto.Hash import SHA
from Crypto.Signature import PKCS1_v1_5
import json

# Helpers
from ..helpers.get_headers import get_headers, with_fingerprint, without_fingerprint

def generate_keys():
    modulus_length = 2048
    key = RSA.generate(modulus_length)
    return key

def encrypt_rsa(a_message, key):
    encryptor = PKCS1_OAEP.new(key)
    encrypted_msg = encryptor.encrypt(bytes(a_message, 'utf-8'))
    encoded_msg = base64.b64encode(encrypted_msg)
    return encoded_msg

def decrypt_rsa(encoded_msg, key):
    encryptor = PKCS1_OAEP.new(key)
    decoded_encrypted_msg = base64.b64decode(encoded_msg)
    decoded_msg = encryptor.decrypt(decoded_encrypted_msg)
    return decoded_msg.decode()

def verify_sign(request, key, endpoint):
    headers = get_headers(request, with_fingerprint)

    pub_key = key[0]
    pub_key = RSA.importKey(pub_key)
    
    try:
        body = request.get_json()
        if body == None:
            body = {}
    except:
        body = {}

    mapped_headers = ""
    mapped_signature_json_check = ""

    for value in headers:
        mapped_headers += f'{value}={headers[value]}' + '&'

    signature_json_check = {
        'headers': mapped_headers,
        'body': f'{json.dupms(body)}',
        'timestamp': str(headers["Timestamp"]),
        'authToken': str(headers["AuthToken"]),
        'endpointUrl': f'{route}/{endpoint}'
    }

    for value in signature_json_check:
        mapped_signature_json_check += f'{value}={signature_json_check[value]}' + '&'

    verifier = PKCS1_v1_5.new(pub_key)
    digest = SHA.new(bytes(mapped_signature_json_check, 'utf-8'))
    print(json.dumps(signature_json_check))
    if verifier.verify(digest, base64.b64decode(request.headers['Signature'])):
        return True
    else:
        return False
