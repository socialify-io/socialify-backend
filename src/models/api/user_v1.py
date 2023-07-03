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
    def build(document: AccountDocument) -> "User":
        return User(
            id=str(document.id),
            username=document.username,
            name=document.name,
            last_name=document.last_name,
            gender=document.gender,
            has_avatar=bool(document.avatar),
        )

    class Config:
        allow_population_by_field_name = True
