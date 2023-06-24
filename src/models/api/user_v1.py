from pydantic import BaseModel, Field, EmailStr

from src.db.documents.account import AccountGender, AccountDocument


class User(BaseModel):
    id: str
    username: str
    name: str = Field(alias="firstName")
    last_name: str = Field(alias="lastName")
    gender: AccountGender
    has_avatar: bool = Field(alias="hasAvatar")

    @staticmethod
    def build(account: AccountDocument) -> "User":
        return User(
            id=str(account.id),
            username=account.username,
            name=account.name,
            last_name=account.last_name,
            gender=account.gender,
            has_avatar=bool(account.avatar),
        )

    class Config:
        allow_population_by_field_name = True
