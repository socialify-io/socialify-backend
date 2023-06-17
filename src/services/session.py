from datetime import datetime, timedelta

import nanoid
from fastapi import Request, Response

from src.db.documents.account import AccountDocument
from src.db.documents.session import SessionDocument


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
            expire_at=utc_now + timedelta(hours=12),
            last_validation_date=utc_now,
            last_active_date=utc_now,
        )
        session.save()
        response.set_cookie("socialify.session", session_id)
        return session
