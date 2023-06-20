from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Query, Request, Depends
from fastapi.responses import RedirectResponse

from src.db.documents.account import AccountDocument
from src.db.documents.oauth2.authorization_code import OAuth2AuthorizationCodeDocument
from src.db.documents.oauth2.client import OAuth2ClientDocument
from src.db.documents.oauth2.token import (
    OAuth2AccessTokenDocument,
    OAuth2RefreshTokenDocument,
)
from src.db.documents.session import SessionDocument
from src.exceptions import OAuth2Exception, APIException
from src.models.api.oauth2_v1 import TokenPayload, TokenResponse
from src.services.account import AccountService
from src.services.oauth2 import OAuth2Service
from src.services.session import SessionService

router: APIRouter = APIRouter(prefix="/oauth2/v1", tags=["api.oauth2.v1"])

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


@router.post("/token")
def get_token(payload: TokenPayload) -> TokenResponse:
    if payload.grant_type == "authorization_code":
        authorization_code: Optional[
            OAuth2AuthorizationCodeDocument
        ] = OAuth2AuthorizationCodeDocument.objects(value=payload.code).first()
        if not authorization_code and authorization_code.expires_at > datetime.utcnow():
            raise OAuth2Exception(
                401, "invalid_grant", "The authorization code is invalid or expired"
            )
        client: Optional[OAuth2ClientDocument] = OAuth2ClientDocument.objects(
            id=payload.client_id
        ).first()
        if (
            not client
            or client.id != authorization_code.client_id
            or not payload.redirect_uri == authorization_code.redirect_uri
        ):
            raise OAuth2Exception(
                401, "unauthorized_client", "Invalid client id or redirect uri"
            )
        account: Optional[AccountDocument] = AccountDocument.objects(
            id=authorization_code.account_id
        ).first()
        if not account:
            raise OAuth2Exception(
                401,
                "invalid_grant",
                "The authorization code is assigned to an account that doesn't exist",
            )
        authorization_code.delete()
        access_token: OAuth2AccessTokenDocument = OAuth2Service.create_access_token(
            client, account, authorization_code.scopes
        )
    elif payload.grant_type == "refresh_token":
        refresh_token: Optional[
            OAuth2RefreshTokenDocument
        ] = OAuth2RefreshTokenDocument.objects(value=payload.refresh_token).first()
        if not refresh_token:
            raise OAuth2Exception(401, "invalid_grant", "The refresh token is invalid")
        access_token: Optional[
            OAuth2AccessTokenDocument
        ] = OAuth2AccessTokenDocument.objects(id=refresh_token.access_token_id).first()
        if not access_token:
            raise OAuth2Exception(
                401,
                "invalid_grant",
                "The refresh token is assigned to an access token that doesn't exist",
            )
        client: Optional[OAuth2ClientDocument] = OAuth2ClientDocument.objects(
            id=payload.client_id
        ).first()
        if not client or client.id != access_token.audience:
            raise APIException(401, "unauthorized_client", "Invalid client id")
        account: Optional[AccountDocument] = AccountDocument.objects(
            id=access_token.subject
        ).first()
        if not account:
            raise OAuth2Exception(
                401,
                "invalid_grant",
                "The refresh token is assigned to an account that doesn't exist",
            )
        refresh_token.delete()
        access_token: OAuth2AccessTokenDocument = OAuth2Service.refresh_access_token(
            access_token
        )
    else:
        raise OAuth2Exception(
            400,
            "unsupported_grant_type",
            f"Grant type {payload.grant_type} is not supported",
        )
    refresh_token: OAuth2RefreshTokenDocument = OAuth2Service.create_refresh_token(
        access_token
    )
    return TokenResponse(
        access_token=access_token.value,
        token_type="Bearer",
        refresh_token=refresh_token.value,
    )
