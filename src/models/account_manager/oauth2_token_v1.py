from datetime import datetime

from pydantic import BaseModel, Field

from src.db.documents.oauth2.client import OAuth2ClientDocument
from src.db.documents.oauth2.token import OAuth2AccessTokenDocument


class Audience(BaseModel):
    id: str
    name: str
    website_url: str = Field(alias="websiteUrl")
    logo_url: str = Field(alias="logoUrl")
    author: str

    @staticmethod
    def build(client_document: OAuth2ClientDocument) -> "Audience":
        return Audience(
            id=str(client_document.id),
            name=client_document.name,
            website_url=client_document.website_url,
            logo_url=client_document.logo_url,
            author=client_document.author
        )

    class Config:
        allow_population_by_field_name = True

class Token(BaseModel):
    id: str
    issuer: str
    audience: Audience
    issued_at: datetime = Field(alias="issuedAt")
    expires_at: datetime = Field(alias="expiresAt")
    last_active_date: datetime = Field(alias="lastActiveDate")
    scopes: list[str]

    @staticmethod
    def build(token_document: OAuth2AccessTokenDocument, client_document: OAuth2ClientDocument) -> "Token":
        return Token(
            id=str(token_document.id),
            issuer=token_document.issuer,
            audience=Audience.build(client_document),
            issued_at=token_document.issued_at,
            expires_at=token_document.expires_at,
            last_active_date=token_document.last_active_date,
            scopes=token_document.scopes
        )


    class Config:
        allow_population_by_field_name = True
