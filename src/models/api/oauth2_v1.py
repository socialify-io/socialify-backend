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
    def build(access_token: OAuth2AccessTokenDocument) -> "TokenData":
        return TokenData(
            jti=str(access_token.id),
            iss=access_token.issuer,
            aud=str(access_token.audience),
            sub=str(access_token.subject),
            iat=access_token.issued_at,
            exp=access_token.expires_at,
            scope=" ".join(access_token.scopes)
        )
