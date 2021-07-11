from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import base64
from Crypto.Hash import SHA
from Crypto.Signature import PKCS1_PSS
import hashlib
import json

def generate_keys():
    modulus_length = 3072
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

def verify_sign(data_to_verify, signature, key):
    verifier = PKCS1_PSS.new(key)
    hasher = SHA.new(bytes(json.dumps(data_to_verify), 'utf-8'))
    print(hasher)
    if verifier.verify(hasher, bytes.fromhex(signature)):
        return True
    else:
        return False