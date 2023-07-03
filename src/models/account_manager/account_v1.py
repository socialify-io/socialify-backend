from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, EmailStr

from src.db.documents.account import AccountGender, AccountDocument


class AccountInfo(BaseModel):
    id: str
    username: str
    email_address: EmailStr = Field(alias="emailAddress")
    name: str = Field(alias="firstName")
    last_name: str = Field(alias="lastName")
    gender: AccountGender
    created_at: datetime = Field(alias="createdAt")
    has_avatar: bool = Field(alias="hasAvatar")

    @staticmethod
    def build(document: AccountDocument) -> "AccountInfo":
        return AccountInfo(
            id=str(document.id),
            username=document.username,
            email_address=document.email_address,
            name=document.name,
            last_name=document.last_name,
            gender=document.gender,
            created_at=document.created_at,
            has_avatar=bool(document.avatar),
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
