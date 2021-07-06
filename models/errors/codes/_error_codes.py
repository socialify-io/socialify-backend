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