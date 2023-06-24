from datetime import datetime

from mongoengine import Document, StringField, ObjectIdField, DateTimeField, ListField


class OAuth2AccessTokenDocument(Document):
    value: str = StringField(unique=True)
    issuer: str = StringField()
    audience: str = ObjectIdField()
    subject: str = ObjectIdField()
    issued_at: datetime = DateTimeField(db_field="issuedAt")
    expires_at: datetime = DateTimeField(db_field="expiresAt")
    last_active_date: datetime = DateTimeField(db_field="lastActiveDate")
    scopes: list[str] = ListField(StringField())
    meta = {"collection": "oauth2-access-token"}


class OAuth2RefreshTokenDocument(Document):
    value: str = StringField(unique=True)
    issuer: str = StringField()
    access_token_id: str = ObjectIdField(db_field="accessTokenId")
    meta = {"collection": "oauth2-refresh-token"}
