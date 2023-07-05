from enum import Enum
from datetime import datetime

from mongoengine import (
    Document,
    StringField,
    EnumField,
    DateTimeField,
    FileField,
    ListField,
)


class AccountGender(Enum):
    MALE = 0
    FEMALE = 1
    OTHER = 2


class AccountDocument(Document):
    username: str = StringField()
    email_address: str = StringField(db_field="emailAddress")
    name: str = StringField()
    last_name: str = StringField(db_field="lastName")
    gender: AccountGender = EnumField(AccountGender)
    hashed_password: str = StringField(db_field="hashedPassword")
    created_at: datetime = DateTimeField(db_field="createdAt")
    last_username_change_date: datetime = DateTimeField(
        db_field="lastUsernameChangeDate"
    )
    avatar = FileField()
    sids: list[str] = ListField(StringField())
    meta = {"collection": "account"}
