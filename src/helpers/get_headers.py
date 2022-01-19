with_device_id = True
without_device_id = False

def get_headers(request, is_with_device_id):
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

    if is_with_device_id:
        headers.update({'DeviceId': request.headers['DeviceId'],
                        'UserId': request.headers['UserId']})

    return headers
