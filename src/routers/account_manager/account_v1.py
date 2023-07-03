from datetime import datetime, timedelta
from typing import Optional

import requests
from fastapi import APIRouter, Body, Request, Response, Depends, UploadFile, File

from src.db.documents.account import AccountDocument
from src.db.documents.oauth2.token import OAuth2AccessTokenDocument
from src.db.documents.session import SessionDocument
from src.exceptions import APIException
from src.models.account_manager.account_v1 import (
    AccountInfo,
    CreateNewAccountPayload,
    UpdateAccountPayload,
)
from src.services.account import AccountService
from src.services.session import SessionService

HCAPTCHA_VERIFY_URL: str = "https://hcaptcha.com/siteverify"
HCAPTCHA_SECRET_KEY: str = "0x0000000000000000000000000000000000000000"

SUPPORTED_AVATAR_MEDIA_TYPES: list[str] = ["image/jpeg", "image/png", "image/gif"]

router: APIRouter = APIRouter(prefix="/account/v1", tags=["account-manager.account.v1"])


def verify_hcaptcha_response(response: str) -> None:
    response = requests.post(
        url=HCAPTCHA_VERIFY_URL,
        data={"secret": HCAPTCHA_SECRET_KEY, "response": response},
    )
    if not response.json()["success"]:
        raise APIException(
            400, "unsuccessful_hcaptcha_response", "hCaptcha verification failed"
        )


@router.post("", status_code=201)
def create_new_account(
    response: Response,
    payload: CreateNewAccountPayload,
    session: Optional[SessionDocument] = Depends(SessionService.get_optional),
) -> None:
    if session:
        SessionService.delete(response, session)
    verify_hcaptcha_response(payload.hcaptcha_response)
    AccountService.create(
        payload.username.strip(),
        payload.email_address.strip(),
        payload.password,
        payload.name.strip(),
        payload.last_name.strip(),
        payload.gender,
    )


@router.get("")
def get_account_info(
    session: SessionDocument = Depends(SessionService.get_required),
) -> AccountInfo:
    account: AccountDocument = AccountService.get_by_session(session)
    return AccountInfo.build(account)


@router.patch("")
def update_account(
    payload: UpdateAccountPayload,
    session: SessionDocument = Depends(SessionService.get_required),
) -> AccountInfo:
    account: AccountDocument = AccountService.get_by_session(session)
    if payload.password:
        if datetime.utcnow() > session.last_validation_date + timedelta(minutes=5):
            raise APIException(
                401, "confirm_identity_required", "Confirm identity is required"
            )
        AccountService.change_password(account, payload.password)
    if payload.username:
        account.update(username=payload.username.strip())
    if payload.name:
        account.update(name=payload.name.strip())
    if payload.last_name:
        account.update(last_name=payload.last_name.strip())
    if payload.gender:
        account.update(gender=payload.gender)
    return AccountInfo.build(account.reload())


@router.delete("")
def delete_account(
    response: Response, session: SessionDocument = Depends(SessionService.get_required)
) -> None:
    account: AccountDocument = AccountService.get_by_session(session)
    if datetime.utcnow() > session.last_validation_date + timedelta(minutes=5):
        raise APIException(
            401, "confirm_identity_required", "Confirm identity is required"
        )
    SessionService.delete(response, session)
    [session.delete() for session in SessionDocument.objects(account_id=account.id)]
    [
        access_token.delete()
        for access_token in OAuth2AccessTokenDocument.objects(subject=account.id)
    ]
    account.delete()


@router.get("/avatar")
def get_account_avatar(session: SessionDocument = Depends(SessionService.get_required)):
    account: AccountDocument = AccountService.get_by_session(session)
    if not bool(account.avatar):
        raise APIException(400, "account_without_avatar", "The account has not avatar")
    return Response(account.avatar.read(), media_type=account.avatar.content_type)


@router.put("/avatar")
async def change_account_avatar(
    file: UploadFile = File(),
    session: SessionDocument = Depends(SessionService.get_required),
) -> None:
    account: AccountDocument = AccountService.get_by_session(session)
    if file.size > 6291456:
        raise APIException(400, "too_big_size", "The avatar can weigh up to 6mb")
    if file.content_type not in SUPPORTED_AVATAR_MEDIA_TYPES:
        raise APIException(415, "unsupported_media_type", "Unsupported Media Type")
    request_object_content = await file.read()
    if account.avatar:
        account.avatar.delete()
    account.avatar.put(request_object_content, content_type=file.content_type)
    account.save()


@router.delete("/avatar")
async def delete_account_avatar(
    session: SessionDocument = Depends(SessionService.get_required),
) -> None:
    account: AccountDocument = AccountService.get_by_session(session)
    account.avatar.delete()
    account.save()
