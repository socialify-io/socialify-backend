class Error(object):
    # Register
    InvalidUsername = 0
    InvalidRepeatPassword = 1

    # Login
    InvalidUsernameOrPassword = 2

    # Crypto
    InvalidPublicRSAKey = 3
    InvalidPasswordEncryption = 4

    # Server
    InternalServerError = 5