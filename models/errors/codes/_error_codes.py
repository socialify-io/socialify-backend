class Error(object):
    # Register
    InvalidUsername = 0
    InvalidRepeatPassword = 1

    # Login
    InvalidUsername = 2
    InvalidPassword = 3

    # Crypto
    InvalidPublicRSAKey = 4
    InvalidPasswordEncryption = 5

    # Server
    InternalServerError = 6

    # Request sign
    InvalidAuthToken = 7
    InvalidHeaders = 8
    InvalidFingerprint = 9
    InvalidSignature = 10
    InvalidRequestPayload = 11