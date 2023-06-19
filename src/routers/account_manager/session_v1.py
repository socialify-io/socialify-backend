from datetime import datetime

from fastapi import APIRouter, Request, Response, Body, Depends

from src.db.documents.account import AccountDocument
from src.db.documents.session import SessionDocument
from src.models.account_manager.account_v1 import AccountInfo
from src.services.account import AccountService
from src.services.session import SessionService

router: APIRouter = APIRouter(prefix="/session/v1", tags=["account-manager.session.v1"])

@router.post("/log-in")
def log_in(
    request: Request,
    response: Response,
    login: str = Body(min_length=5, max_length=20),
    password: str = Body(min_length=10),
) -> AccountInfo:
    account: AccountDocument = AccountService.authenticate(login, password)
    SessionService.create(request, response, account)
    return AccountInfo.build(account)

@router.post("/log-out")
def log_out(
    response: Response, session: SessionDocument = Depends(SessionService.get_required)
) -> None:
    SessionService.delete(response, session)


@router.post("/confirm-identity")
def confirm_identity(
    password: str = Body(min_length=10),
    session: SessionDocument = Depends(SessionService.get_required),
) -> None:
    account: AccountDocument = AccountService.get_by_session(session)
    AccountService.verify_password(account, password)
    session.update(last_validation_date=datetime.utcnow())
