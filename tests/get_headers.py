import datetime
import bcrypt

def get_headers(endpoint):
    timestamp = int(datetime.datetime.now().timestamp())

    auth_token_begin_header = f'$begin-{endpoint}$'
    auth_token_end_header = f'$end-{endpoint}$'

    os = 'iOS_14.6'
    app_version = '0.1'
    user_agent = 'Socialify-iOS'

    auth_token = bytes(
        f'{auth_token_begin_header}.{app_version}+{os}+{user_agent}#{timestamp}#.{auth_token_end_header}', 'utf-8')

    auth_token_hashed = bcrypt.hashpw(auth_token, bcrypt.gensalt())

    headers = {
        'Content-Type': 'applictaion/json',
        'User-Agent': user_agent,
        'OS': os,
        'Timestamp': timestamp,
        'AppVersion': app_version,
        'AuthToken': auth_token_hashed.decode(),
    }

    return headers
