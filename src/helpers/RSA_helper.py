from app import route
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import base64
from Crypto.Hash import SHA
from Crypto.Signature import PKCS1_PSS
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
    encoded_encrypted_msg = base64.b64encode(encrypted_msg)
    return encoded_encrypted_msg

def decrypt_rsa(encoded_encrypted_msg, key):
    encryptor = PKCS1_OAEP.new(key)
    decoded_encrypted_msg = base64.b64decode(encoded_encrypted_msg)
    decoded_decrypted_msg = encryptor.decrypt(decoded_encrypted_msg)
    return decoded_decrypted_msg.decode()

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

    signature_json_check = {
        'headers': headers,
        'body': body,
        'timestamp': headers["Timestamp"],
        'authToken': headers["AuthToken"],
        'endpointUrl': f'{route}/{endpoint}'
    }

    verifier = PKCS1_PSS.new(pub_key)
    digest = SHA.new(bytes(json.dumps(signature_json_check), 'utf-8'))
    print(digest)
    if verifier.verify(digest, bytes.fromhex(request.headers['Signature'])):
        return True
    else:
        return False