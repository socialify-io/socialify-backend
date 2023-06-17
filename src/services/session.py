from datetime import datetime, timedelta
from typing import Optional

import nanoid
from fastapi import Request, Response

from src.db.documents.account import AccountDocument
from src.db.documents.session import SessionDocument
from src.exceptions import APIException


class SessionService:
    @staticmethod
    def create(request: Request, response: Response, account: AccountDocument) -> SessionDocument:
        while True:
            session_id = nanoid.generate(size=96)
            if not SessionDocument.objects(id=session_id):
                break
        utc_now: datetime = datetime.utcnow()
        session: SessionDocument = SessionDocument(
            id=session_id,
            ip_address=request.client.host,
            user_agent=request.headers.get("User-Agent"),
            account_id=account.id,
            created_at=utc_now,
            expires_at=utc_now + timedelta(hours=12),
            last_validation_date=utc_now,
            last_active_date=utc_now,
        )
        session.save()
        response.set_cookie("socialify.session", session_id)
        return session

    @staticmethod
    def get_required(request: Request) -> SessionDocument:
        session_id = request.cookies.get("socialify.session")
        session: Optional[SessionDocument] = SessionDocument.objects(id=session_id).first()
        if session and datetime.utcnow() < session.expires_at:
            expires_at: datetime = datetime.utcnow() + timedelta(hours=12)
            session.update(expires_at=expires_at, last_active_date=datetime.utcnow())
            return session
        raise APIException(
            401, "unauthorized", "The session does not exist or has expired"
        )

    @staticmethod
    def delete(response: Response, session: SessionDocument) -> None:
        session.delete()
        response.delete_cookie("socialify.session")
