from datetime import datetime

from pydantic import BaseModel, Field

from src.db.documents.account import AccountGender, AccountDocument


class AccountInfo(BaseModel):
    id: str
    username: str
    email_address: str = Field(alias="emailAddress")
    name: str = Field(alias="firstName")
    last_name: str = Field(alias="lastName")
    gender: AccountGender
    created_at: datetime = Field(alias="createdAt")

    @staticmethod
    def build(account: AccountDocument) -> "AccountInfo":
        return AccountInfo(
            id=str(account.id),
            username=account.username,
            email_address=account.email_address,
            name=account.name,
            last_name=account.last_name,
            gender=account.gender,
            created_at=account.created_at
        )

    class Config:
        allow_population_by_field_name = True
