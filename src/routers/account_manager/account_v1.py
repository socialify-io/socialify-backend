from datetime import datetime, timedelta
from typing import Optional

import requests
from fastapi import APIRouter, Body, Request, Response, Depends
from pydantic import BaseModel, Field, EmailStr

from src.db.documents.account import AccountGender, AccountDocument
from src.db.documents.session import SessionDocument
from src.exceptions import APIException
from src.models.account_manager.account_info import AccountInfo
from src.services.account import AccountService
from src.services.session import SessionService

HCAPTCHA_VERIFY_URL: str = "https://hcaptcha.com/siteverify"
HCAPTCHA_SECRET_KEY: str = "0x0000000000000000000000000000000000000000"

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


class CreateNewAccountPayload(BaseModel):
    username: str = Field(min_length=5, max_length=20)
    email_address: EmailStr = Field(alias="emailAddress")
    password: str = Field(min_length=10)
    name: str
    last_name: str = Field(alias="lastName")
    gender: AccountGender
    hcaptcha_response: str = Field(alias="hcaptchaResponse")


class UpdateAccountPayload(BaseModel):
    username: Optional[str] = Field(min_length=5, max_length=20, default=None)
    password: Optional[str] = Field(min_length=10, default=None)
    name: Optional[str] = None
    last_name: Optional[str] = Field(alias="lastName", default=None)
    gender: Optional[AccountGender] = None


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
    account.delete()


@router.post("/log-in")
def log_in(
    request: Request,
    response: Response,
    login: str = Body(min_length=5, max_length=20),
    password: str = Body(min_length=10),
) -> AccountInfo:
    account: AccountDocument = AccountService.authenticate(login, password)
    SessionService.create(request, response, account)
    return AccountInfo.build(account)


@router.post("/log-out")
def log_out(
    response: Response, session: SessionDocument = Depends(SessionService.get_required)
) -> None:
    SessionService.delete(response, session)

@router.post("/confirm-identity")
def confirm_identity(
        password: str = Body(min_length=10), session: SessionDocument = Depends(SessionService.get_required)) -> None:
    account: AccountDocument = AccountService.get_by_session(session)
    AccountService.verify_password(account, password)
    session.update(last_validation_date=datetime.utcnow())
