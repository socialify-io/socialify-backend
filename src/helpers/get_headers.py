with_fingerprint = True
without_fingerprint = False

def get_headers(request, is_with_fingerprint):
    print(request.headers)
    headers = {
        'Content-Type': request.headers['Content-Type'],
        'User-Agent': request.headers['User-Agent'],
        'OS': request.headers['OS'],
        'Timestamp': int(request.headers['Timestamp']),
        'AppVersion': request.headers['AppVersion'],
        'AuthToken': request.headers['AuthToken'],
        'Accept': request.headers['Accept']
    }

    if is_with_fingerprint:
        headers.update({'Fingerprint': request.headers['Fingerprint'],
                        'DeviceId': request.headers['DeviceId']})

    return headers
