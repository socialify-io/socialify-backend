class ApiError(object):
    def __init__(self, code, reason):
        self.code = code
        self.reason = reason