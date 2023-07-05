from fastapi import APIRouter, Depends
from fastapi.websockets import WebSocket, WebSocketDisconnect

from src.db.documents.account import AccountDocument
from src.db.documents.oauth2.token import OAuth2AccessTokenDocument
from src.services.account import AccountService
from src.services.oauth2 import OAuth2Service
from src.services.websocket_connection import service as connection_service

router: APIRouter = APIRouter(
    prefix="/websocket/v1", tags=["api.messenger.websocket.v1"]
)


@router.websocket("")
async def websocket(
    websocket: WebSocket,
    access_token: OAuth2AccessTokenDocument = Depends(
        OAuth2Service.get_access_token_by_header
    ),
):
    account: AccountDocument = AccountService.get_by_access_token(access_token)
    await connection_service.connect(websocket, account)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        connection_service.disconnect(websocket, account)
