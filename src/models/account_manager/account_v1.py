from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, EmailStr

from src.db.documents.account import AccountGender, AccountDocument


class AccountInfo(BaseModel):
    id: str
    username: str
    email_address: str = Field(alias="emailAddress")
    name: str = Field(alias="firstName")
    last_name: str = Field(alias="lastName")
    gender: AccountGender
    created_at: datetime = Field(alias="createdAt")
    has_avatar: bool = Field(alias="hasAvatar")

    @staticmethod
    def build(account: AccountDocument) -> "AccountInfo":
        return AccountInfo(
            id=str(account.id),
            username=account.username,
            email_address=account.email_address,
            name=account.name,
            last_name=account.last_name,
            gender=account.gender,
            created_at=account.created_at,
            has_avatar=bool(account.avatar),
        )

    class Config:
        allow_population_by_field_name = True


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
