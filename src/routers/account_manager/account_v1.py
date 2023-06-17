import requests
from fastapi import APIRouter, Body, Request, Response
from pydantic import BaseModel, Field, EmailStr

from src.db.documents.account import AccountGender, AccountDocument
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
        raise APIException(400, "unsuccessful_hcaptcha_response", "hCaptcha verification failed")


class CreateNewAccountPayload(BaseModel):
    username: str = Field(min_length=5, max_length=20)
    email_address: EmailStr = Field(alias="emailAddress")
    password: str = Field(min_length=10)
    name: str
    last_name: str = Field(alias="lastName")
    gender: AccountGender
    hcaptcha_response: str = Field(alias="hcaptchaResponse")


@router.post("", status_code=201)
def create_new_account(payload: CreateNewAccountPayload) -> None:
    verify_hcaptcha_response(payload.hcaptcha_response)
    AccountService.create(
        payload.username.strip(),
        payload.email_address.strip(),
        payload.password,
        payload.name.strip(),
        payload.last_name.strip(),
        payload.gender,
    )

@router.post("/log-in")
def log_in(request: Request, response: Response, login: str = Body(min_length=5, max_length=20),
           password: str = Body(min_length=10)) -> AccountInfo:
    account: AccountDocument = AccountService.authenticate(login, password)
    SessionService.create(request, response, account)
    return AccountInfo.build(account)
