from datetime import datetime

import bcrypt

from src.db.documents.account import AccountGender, AccountDocument
from src.exceptions import APIException


class AccountService:
    @staticmethod
    def create(
        username: str,
        email_address: str,
        password: str,
        name: str,
        last_name: str,
        gender: AccountGender,
    ) -> None:
        if AccountDocument.objects(username=username):
            raise APIException(400, "taken_username", "The username is already taken")
        if AccountDocument.objects(email_address=email_address):
            raise APIException(
                400, "taken_email_address", "The email address is already taken"
            )
        hashed_password: str = bcrypt.hashpw(
            password.encode(), bcrypt.gensalt()
        ).decode()
        now: datetime = datetime.utcnow()
        AccountDocument(
            username=username,
            email_address=email_address,
            hashed_password=hashed_password,
            name=name,
            last_name=last_name,
            gender=gender,
            created_at=now,
            last_username_change_date=now,
        ).save()
