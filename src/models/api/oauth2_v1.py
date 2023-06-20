from typing import Optional

from pydantic import BaseModel


class TokenPayload(BaseModel):
    grant_type: str
    code: Optional[str] = None
    refresh_token: Optional[str] = None
    redirect_uri: Optional[str] = None
    client_id: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str
