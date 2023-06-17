class APIException(Exception):
    def __init__(self, status_code: int, code: str, message: str):
        self.status_code: int = status_code
        self.code: str = code
        self.message: str = message
