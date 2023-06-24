from datetime import datetime, timedelta

import nanoid
from fastapi import Header

from src.db.documents.account import AccountDocument
from src.db.documents.oauth2.authorization_code import OAuth2AuthorizationCodeDocument
from src.db.documents.oauth2.client import OAuth2ClientDocument
from src.db.documents.oauth2.token import (
    OAuth2AccessTokenDocument,
    OAuth2RefreshTokenDocument,
)
from src.exceptions import APIException


class OAuth2Service:
    @staticmethod
    def create_authorization_code(
        account: AccountDocument,
        client: OAuth2ClientDocument,
        redirect_uri: str,
        scopes: list[str],
    ) -> OAuth2AuthorizationCodeDocument:
        while True:
            code_value = nanoid.generate(size=96)
            if not OAuth2AuthorizationCodeDocument.objects(value=code_value):
                break
        now: datetime = datetime.utcnow()
        authorization_code: OAuth2AuthorizationCodeDocument = (
            OAuth2AuthorizationCodeDocument(
                value=code_value,
                scopes=scopes,
                account_id=account.id,
                client_id=client.id,
                issued_at=now,
                expires_at=now + timedelta(minutes=2),
                redirect_uri=redirect_uri,
                issuer="me.socialify.oauth2",
            ).save()
        )
        return authorization_code

    @staticmethod
    def create_access_token(
        client: OAuth2ClientDocument, account: AccountDocument, scopes: list[str]
    ) -> OAuth2AccessTokenDocument:
        while True:
            token_value = nanoid.generate(size=2048)
            if not OAuth2AccessTokenDocument.objects(value=token_value):
                break
        now: datetime = datetime.utcnow()
        access_token: OAuth2AccessTokenDocument = OAuth2AccessTokenDocument(
            value=token_value,
            issuer="me.socialify.oauth2",
            audience=client.id,
            subject=account.id,
            issued_at=now,
            expires_at=now + timedelta(hours=6),
            scopes=scopes,
        ).save()
        return access_token

    @staticmethod
    def create_refresh_token(
        access_token: OAuth2AccessTokenDocument,
    ) -> OAuth2RefreshTokenDocument:
        while True:
            token_value = nanoid.generate(size=2048)
            if not OAuth2RefreshTokenDocument.objects(value=token_value):
                break
        refresh_token: OAuth2RefreshTokenDocument = OAuth2RefreshTokenDocument(
            value=token_value,
            issuer="me.socialify.oauth2",
            access_token_id=access_token.id,
        ).save()
        return refresh_token

    @staticmethod
    def refresh_access_token(
        access_token: OAuth2AccessTokenDocument,
    ) -> OAuth2AccessTokenDocument:
        while True:
            token_value = nanoid.generate(size=2048)
            if not OAuth2AccessTokenDocument.objects(value=token_value):
                break
        access_token.update(
            value=token_value, expires_at=datetime.utcnow() + timedelta(hours=6)
        )
        return access_token

    @staticmethod
    def get_access_token_by_header(
        value: str = Header(alias="X-Access-Token"),
    ) -> OAuth2AccessTokenDocument:
        access_token: OAuth2AccessTokenDocument = OAuth2AccessTokenDocument.objects(
            value=value
        ).first()
        if not access_token or datetime.utcnow() >= access_token.expires_at:
            raise APIException(
                401, "unauthorized", "The access token is invalid or expired"
            )
        access_token.update(last_active_date=datetime.utcnow())
        return access_token
