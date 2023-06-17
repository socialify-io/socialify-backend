from typing import Any

from pydantic import BaseModel


class APIError(BaseModel):
    code: str
    message: Any
