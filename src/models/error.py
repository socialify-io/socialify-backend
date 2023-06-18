from typing import Any

from pydantic import BaseModel


class APIError(BaseModel):
    code: str
    message: Any


class OAuth2Error(BaseModel):
    error_code: str
    error_description: str
