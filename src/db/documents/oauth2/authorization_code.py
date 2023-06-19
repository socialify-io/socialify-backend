from datetime import datetime

from mongoengine import Document, ObjectIdField, DateTimeField, StringField, ListField


class OAuth2AuthorizationCodeDocument(Document):
    value = StringField(unique=True)
    scopes: list[str] = ListField(StringField())
    account_id: str = ObjectIdField(db_field="accountId")
    client_id: str = ObjectIdField(db_field="clientId")
    issued_at: datetime = DateTimeField(db_field="issuedAt")
    expires_at: datetime = DateTimeField(db_field="expiresAt")
    redirect_uri: str = StringField(db_field="redirectUri")
    issuer: str = StringField()
    meta = {"collection": "oauth2-authorization-code"}
