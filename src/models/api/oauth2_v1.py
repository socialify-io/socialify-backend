from typing import Optional

from pydantic import BaseModel

from src.db.documents.oauth2.token import OAuth2AccessTokenDocument


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


class TokenData(BaseModel):
    jti: str
    iss: str
    aud: str
    sub: str
    iat: int
    exp: int
    scope: str

    @staticmethod
    def build(document: OAuth2AccessTokenDocument) -> "TokenData":
        return TokenData(
            jti=str(document.id),
            iss=document.issuer,
            aud=str(document.audience),
            sub=str(document.subject),
            iat=document.issued_at.timestamp(),
            exp=document.expires_at.timestamp(),
            scope=" ".join(document.scopes),
        )
