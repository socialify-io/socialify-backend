import bcrypt

def verify_authtoken(headers, endpoint):
    auth_token_check = bytes(
        f'$begin-{endpoint}$.{headers["AppVersion"]}+{headers["OS"]}+{headers["User-Agent"]}#{headers["Timestamp"]}#.$end-{endpoint}$', 'utf-8')

    if bcrypt.checkpw(auth_token_check, bytes(headers["AuthToken"], 'utf-8')):
        return True
    else: 
        return False
