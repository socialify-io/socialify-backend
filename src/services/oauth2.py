from datetime import datetime, timedelta

import nanoid

from src.db.documents.account import AccountDocument
from src.db.documents.oauth2.authorization_code import OAuth2AuthorizationCodeDocument
from src.db.documents.oauth2.client import OAuth2ClientDocument


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
                expire_at=now + timedelta(minutes=2),
                redirect_uri=redirect_uri,
                issuer="me.socialify.oauth2",
            )
        )
        return authorization_code
