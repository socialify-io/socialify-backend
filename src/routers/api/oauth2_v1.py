from typing import Optional

from fastapi import APIRouter, Query, Request, Depends
from fastapi.responses import RedirectResponse

from src.db.documents.account import AccountDocument
from src.db.documents.oauth2.authorization_code import OAuth2AuthorizationCodeDocument
from src.db.documents.oauth2.client import OAuth2ClientDocument
from src.db.documents.session import SessionDocument
from src.services.account import AccountService
from src.services.oauth2 import OAuth2Service
from src.services.session import SessionService

router: APIRouter = APIRouter(prefix="/oauth2/v1")

API_SCOPES: dict[str, str] = {"user:profile": "Read user profile data."}
ACCOUNT_MANAGER_FRONTEND: str = "http://account-manager.localhost:8000"

@router.get("/authorize")
def authorize(
    request: Request,
    response_type: str,
    client_id: str,
    redirect_uri: str,
    state: str,
    scopes: list[str] = Query(alias="scope"),
    session: Optional[SessionDocument] = Depends(SessionService.get_optional),
) -> RedirectResponse:
    account: AccountDocument = AccountService.get_by_session(session)
    client: Optional[OAuth2ClientDocument] = OAuth2ClientDocument.objects(
        id=client_id
    ).first()
    if not client or redirect_uri not in client.redirect_uris:
        return RedirectResponse(
            f"{ACCOUNT_MANAGER_FRONTEND}/oauth2/error?code=unauthorized_client"
        )
    if response_type != "code":
        return RedirectResponse(f"{redirect_uri}?error=unsupported_response_type")
    for scope in scopes:
        if scope not in API_SCOPES:
            return RedirectResponse(f"{redirect_uri}?error=invalid_scope")
    if not session:
        return RedirectResponse(
            f"{ACCOUNT_MANAGER_FRONTEND}/account/log-in?continue={request.url.path}"
        )
    authorization_code: OAuth2AuthorizationCodeDocument = (
        OAuth2Service.create_authorization_code(account, client, redirect_uri, scopes)
    )
    return RedirectResponse(
        f"{redirect_uri}?code={authorization_code.value}&state={state}"
    )
