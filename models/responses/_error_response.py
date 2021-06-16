class ErrorResponse(object):
    def __init__(self, errors):
        self.errors = errors
        self.success = False