from typing import Any

from fastapi.websockets import WebSocket

from src.db.documents.account import AccountDocument


class WebSocketConnectionService:
    def __init__(self):
        self.connections: dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, account: AccountDocument) -> None:
        await websocket.accept()
        self.connections[str(id(websocket))] = websocket
        account.update(push__sids=str(id(websocket)))

    def disconnect(self, websocket: WebSocket, account: AccountDocument) -> None:
        self.connections.pop(str(id(websocket)))
        account.update(pull__sids=str(id(websocket)))

    def get_connections_by_account(self, account: AccountDocument) -> list[WebSocket]:
        return [self.connections[sid] for sid in account.sids]

    @staticmethod
    async def emit(websocket: WebSocket, event: str, data: Any) -> None:
        await websocket.send_json({"event": event, "data": data})


service: WebSocketConnectionService = WebSocketConnectionService()
