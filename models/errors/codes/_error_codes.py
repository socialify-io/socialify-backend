class Error(object):
    # Register
    InvalidUsername = 1
    InvalidRepeatPassword = 2

    # Login
    InvalidPassword = 3

    # Crypto
    InvalidPublicRSAKey = 4
    InvalidPasswordEncryption = 5

    # Server
    InternalServerError = 6
    BadRequest = 7

    # Request sign
    InvalidAuthToken = 8
    InvalidHeaders = 9
    InvalidFingerprint = 10
    InvalidDeviceId = 11
    InvalidSignature = 12
    InvalidRequestPayload = 13