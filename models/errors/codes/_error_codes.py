class Error(object):
    # Register
    InvalidUsername = 1
    InvalidRepeatPassword = 2

    # Login
    InvalidUsername = 3
    InvalidPassword = 4

    # Crypto
    InvalidPublicRSAKey = 5
    InvalidPasswordEncryption = 6

    # Server
    InternalServerError = 7

    # Request sign
    InvalidAuthToken = 8
    InvalidHeaders = 9
    InvalidFingerprint = 10
    InvalidSignature = 11
    InvalidRequestPayload = 12