from datetime import datetime
from typing import Optional

import bcrypt

from src.db.documents.account import AccountGender, AccountDocument
from src.db.documents.oauth2.token import OAuth2AccessTokenDocument
from src.db.documents.session import SessionDocument
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

    @staticmethod
    def authenticate(login: str, password: str) -> AccountDocument:
        account: AccountDocument = AccountService.get_by_username_or_email_address(
            login
        )
        AccountService.verify_password(account, password)
        return account

    @staticmethod
    def get_by_username_or_email_address(login: str) -> AccountDocument:
        account: Optional[AccountDocument] = AccountDocument.objects(
            username=login
        ).first()
        if account:
            return account
        account: Optional[AccountDocument] = AccountDocument.objects(
            email_address=login
        ).first()
        if not account:
            raise APIException(
                401, "incorrect_credentials", "login or password is incorrect"
            )
        return account

    @staticmethod
    def verify_password(account: AccountDocument, password: str) -> None:
        if not bcrypt.checkpw(password.encode(), account.hashed_password.encode()):
            raise APIException(
                401, "incorrect_credentials", "login or password is incorrect"
            )

    @staticmethod
    def get_by_session(session: SessionDocument) -> AccountDocument:
        account: Optional[AccountDocument] = AccountDocument.objects(
            id=session.account_id
        ).first()
        if not account:
            raise APIException(
                401,
                "invalid_session",
                "The session is assigned to an account that doesn't exist",
            )
        return account

    @staticmethod
    def change_password(account: AccountDocument, password: str) -> None:
        hashed_password: str = bcrypt.hashpw(
            password.encode(), bcrypt.gensalt()
        ).decode()
        account.modify(hashed_password=hashed_password)

    @staticmethod
    def get_by_access_token(access_token: OAuth2AccessTokenDocument) -> AccountDocument:
        account: Optional[AccountDocument] = AccountDocument.objects(
            id=access_token.subject
        ).first()
        if not account:
            raise APIException(
                401,
                "invalid_access_token",
                "The access token is assigned to an account that doesn't exist",
            )
        return account
