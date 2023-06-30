from typing import Optional

from fastapi import APIRouter, Depends

from src.db.documents.account import AccountDocument
from src.db.documents.oauth2.client import OAuth2ClientDocument
from src.db.documents.oauth2.token import OAuth2AccessTokenDocument, OAuth2RefreshTokenDocument
from src.db.documents.session import SessionDocument
from src.exceptions import APIException
from src.models.account_manager.oauth2_token_v1 import Token
from src.services.account import AccountService
from src.services.session import SessionService

router: APIRouter = APIRouter(prefix="/oauth2-token/v1", tags=["account-manager.oauth2-token.v1"])

@router.get("")
def get_tokens(session: SessionDocument = Depends(SessionService.get_required)) -> list[Token]:
    account: AccountDocument = AccountService.get_by_session(session)
    tokens: list[OAuth2AccessTokenDocument] = OAuth2AccessTokenDocument.objects(subject=account.id)
    return [Token.build(token, OAuth2ClientDocument.objects(id=token.audience).first()) for token in tokens]

@router.delete("/{token_id}")
def delete_token(token_id: str, session: SessionDocument = Depends(SessionService.get_required)):
    account: AccountDocument = AccountService.get_by_session(session)
    token: Optional[OAuth2AccessTokenDocument] = OAuth2AccessTokenDocument.objects(id=token_id, subject=account.id).first()
    if not token:
        raise APIException(400, "invalid_token", "Invalid token id")
    refresh_token: OAuth2RefreshTokenDocument = OAuth2RefreshTokenDocument.objects(access_token_id=token.id).first()
    token.delete()
    refresh_token.delete()
